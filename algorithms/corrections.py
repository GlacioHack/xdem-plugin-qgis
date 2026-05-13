import os
import xdem
from qgis.core import (
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterRasterDestination,
)
from .processing_tools import XdemProcessingAlgorithm, coreg_info, load_mask

# Dictionaries listing bias correction and coregistration methods

BIAS_METHODS = {
    "Deramping": xdem.coreg.Deramp(),
    "Directional biases": xdem.coreg.DirectionalBias(),
    "Terrain biases": xdem.coreg.TerrainBias(),
}


COREG_METHODS = {
    "Nuth and Kääb (2011)": xdem.coreg.NuthKaab(),
    "Minimization of dh": xdem.coreg.DhMinimize(),
    "Least Z-difference": xdem.coreg.LZD(),
    "Iterative closest point": xdem.coreg.ICP(),
    "Coherent point drift": xdem.coreg.CPD(),
    "Vertical shift": xdem.coreg.VerticalShift(),
}


class BiasCorrection(XdemProcessingAlgorithm):
    """
    This class is designed to correct elevation errors using various bias correction methods.
    """

    def initAlgorithm(self, config=None):
        """
        Function to retrieve parameters entered in QGIS.
        :param TBA_DEM: The DEM requiring correction.
        :param REF_DEM: The reference DEM.
        :param MASK: An optional inlier mask used to define reliable data points (0 for outliers, 1 for inliers)
        :param METHOD: Specifies the bias correction method (e.g., "Deramping", "Directional biases").
        :param OUTPUT: The aligned DEM.
        """

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="TBA_DEM", description="DEM to be aligned"
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="REF_DEM", description="Reference DEM"
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="MASK", description="Inlier mask", defaultValue=None, optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name="METHOD",
                description="Method",
                options=BIAS_METHODS,
                defaultValue="Deramping",
                usesStaticStrings=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                name="OUTPUT", description="Aligned DEM"
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Loading layers from QGIS
        tba_dem_layer = self.parameterAsRasterLayer(parameters, "TBA_DEM", context)
        ref_dem_layer = self.parameterAsRasterLayer(parameters, "REF_DEM", context)

        # Extracting paths
        tba_dem_path = tba_dem_layer.dataProvider().dataSourceUri()
        ref_dem_path = ref_dem_layer.dataProvider().dataSourceUri()

        method = self.parameterAsString(parameters, "METHOD", context)
        output_path = self.parameterAsOutputLayer(parameters, "OUTPUT", context)

        tba_dem = xdem.DEM(tba_dem_path)
        ref_dem = xdem.DEM(ref_dem_path)

        inlier_mask = load_mask(self, parameters, context, feedback)

        # Loading the corresponding method
        coreg = BIAS_METHODS[method]

        coreg.fit(ref_dem, tba_dem, inlier_mask)
        aligned_dem = coreg.apply(tba_dem)

        # Display the bias corrections informations in the QGIS console
        feedback.pushInfo("Bias corrections informations:")
        coreg_info(coreg, feedback)

        aligned_dem.to_file(output_path)

        return {"OUTPUT": output_path}

    def name(self):
        return "Bias correction"

    def groupId(self):
        return "Corrections"

    def tags(self):
        return BIAS_METHODS

    def shortHelpString(self):
        return (
            "This algorithm aim at correcting both systematic elevation errors and spatially-structured random errors.\n"
            "Bias-correction methods correspond to transformations that cannot be described as a 3D affine transformations."
        )

    def createInstance(self):
        return BiasCorrection()


class Coregistration(XdemProcessingAlgorithm):
    """
    This class is designed to correct elevation errors using affine coregistration methods.
    """

    def initAlgorithm(self, config=None):
        """
        Function to retrieve parameters entered in QGIS.
        :param TBA_DEM: The DEM requiring correction.
        :param REF_DEM: The reference DEM.
        :param MASK: An optional inlier mask used to define reliable data points (0 for outliers, 1 for inliers)
        :param METHOD: Specifies the coregistration method (e.g., "Nuth and Kääb (2011)", "Iterative closest point").
        :param BLOCKSIZE: Block size for blockwise execution.
        :param OUTPUT: The aligned DEM.
        """

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="TBA_DEM", description="DEM to be aligned"
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="REF_DEM", description="Reference DEM"
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="MASK", description="Inlier mask", defaultValue=None, optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name="METHOD",
                description="Method",
                options=COREG_METHODS,
                defaultValue="Nuth and Kääb (2011)",
                usesStaticStrings=True,
            )
        )

        parameter = QgsProcessingParameterNumber(
            name="BLOCKSIZE", description="Blocksize", optional=True
        )
        parameter.setFlags(
            parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(parameter)

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                name="OUTPUT", description="Aligned DEM"
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Loading layers from QGIS
        tba_dem_layer = self.parameterAsRasterLayer(parameters, "TBA_DEM", context)
        ref_dem_layer = self.parameterAsRasterLayer(parameters, "REF_DEM", context)

        # Extracting paths
        tba_dem_path = tba_dem_layer.dataProvider().dataSourceUri()
        ref_dem_path = ref_dem_layer.dataProvider().dataSourceUri()

        method = self.parameterAsString(parameters, "METHOD", context)
        block_size = self.parameterAsInt(parameters, "BLOCKSIZE", context)
        output_path = self.parameterAsOutputLayer(parameters, "OUTPUT", context)

        tba_dem = xdem.DEM(tba_dem_path)
        ref_dem = xdem.DEM(ref_dem_path)

        inlier_mask = load_mask(self, parameters, context, feedback)

        coreg = COREG_METHODS[method]

        feedback.pushInfo("Curently, Blockwise work only with Nuth and Kääb (2011).")

        # Configuring blockwise if a block size is specified and if Nuth and Kääb is config
        if block_size != 0 and method == "Nuth and Kääb (2011)":
            blockwise = xdem.coreg.BlockwiseCoreg(
                coreg,
                block_size_fit=block_size,
                block_size_apply=block_size,
                parent_path=os.path.dirname(__file__),
            )
            blockwise.fit(ref_dem, tba_dem, inlier_mask)
            aligned_dem = blockwise.apply()
        else:
            coreg.fit(ref_dem, tba_dem, inlier_mask)
            aligned_dem = coreg.apply(tba_dem)

            # Display the coregistration informations in the QGIS console
            feedback.pushInfo("Coregistration informations:")
            coreg_info(coreg, feedback)

        aligned_dem.to_file(output_path)

        return {"OUTPUT": output_path}

    def name(self):
        return "Coregistration"

    def groupId(self):
        return "Corrections"

    def tags(self):
        return COREG_METHODS

    def shortHelpString(self):
        return (
            "This algorithm enables the coregistration of two DEMs by applying 3D affine transformations.\n"
            "Affine transformations can include vertical and horizontal translations, rotations and reflections, and scalings.\n"
        )

    def createInstance(self):
        return Coregistration()


class GapFilling(XdemProcessingAlgorithm):
    """
    This class is designed to fill in gaps in the DEM using an IDW method.
    """

    def initAlgorithm(self, config=None):
        """
        Function to retrieve parameters entered in QGIS.
        :param TBF_DEM: The DEM to be filled out.
        :param OUTPUT: The filled DEM.
        """

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="TBF_DEM", description="DEM to be filled"
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                name="OUTPUT", description="Filled DEM"
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Loading layer from QGIS
        dem_layer = self.parameterAsRasterLayer(parameters, "TBF_DEM", context)

        # Extracting path
        dem_path = dem_layer.dataProvider().dataSourceUri()

        output_path = self.parameterAsOutputLayer(parameters, "OUTPUT", context)

        dem = xdem.DEM(dem_path)

        # Conversion to DEM difference object
        ddem = xdem.dDEM(raster=dem, start_time=None, end_time=None)

        filled_array = ddem.interpolate(method="idw")

        # Interpolation returns an array, it must be converted to a DEM
        filled_dem = xdem.DEM.from_array(
            filled_array, transform=dem.transform, crs=dem.crs
        )

        filled_dem.to_file(output_path)

        return {"OUTPUT": output_path}

    def name(self):
        return "Gap filling"

    def groupId(self):
        return "Corrections"

    def shortHelpString(self):
        return (
            "This algorithm uses the IDW (Inverse-distance weighting) method.\n"
            "Empty areas are filled with a weighted average of the surrounding pixel values, "
            "with the weight being inversely proportional to their distance from the empty pixel."
        )

    def createInstance(self):
        return GapFilling()
