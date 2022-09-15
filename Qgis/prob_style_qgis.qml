<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis minScale="1e+08" maxScale="0" styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="0" version="3.22.10-Białowieża">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal enabled="0" fetchMode="0" mode="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option value="false" name="WMSBackgroundLayer" type="QString"/>
      <Option value="false" name="WMSPublishDataSourceUrl" type="QString"/>
      <Option value="0" name="embeddedWidgets/count" type="QString"/>
      <Option value="Value" name="identify/format" type="QString"/>
    </Option>
  </customproperties>
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option value="" name="name" type="QString"/>
      <Option name="properties"/>
      <Option value="collection" name="type" type="QString"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling enabled="false" maxOversampling="2" zoomedInResamplingMethod="nearestNeighbour" zoomedOutResamplingMethod="nearestNeighbour"/>
    </provider>
    <rasterrenderer alphaBand="-1" opacity="1" nodataColor="" band="1" classificationMax="10000" type="singlebandpseudocolor" classificationMin="0">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <rastershader>
        <colorrampshader maximumValue="10000" colorRampType="INTERPOLATED" clip="0" labelPrecision="0" classificationMode="1" minimumValue="0">
          <colorramp name="[source]" type="gradient">
            <Option type="Map">
              <Option value="34,139,34,255" name="color1" type="QString"/>
              <Option value="0,0,0,255" name="color2" type="QString"/>
              <Option value="0" name="discrete" type="QString"/>
              <Option value="gradient" name="rampType" type="QString"/>
              <Option value="0.005;255,165,0,255:0.01;215,25,28,255" name="stops" type="QString"/>
            </Option>
            <prop k="color1" v="34,139,34,255"/>
            <prop k="color2" v="0,0,0,255"/>
            <prop k="discrete" v="0"/>
            <prop k="rampType" v="gradient"/>
            <prop k="stops" v="0.005;255,165,0,255:0.01;215,25,28,255"/>
          </colorramp>
          <item color="#228b22" value="0" label="0" alpha="255"/>
          <item color="#ffa500" value="50" label="50" alpha="255"/>
          <item color="#d7191c" value="100" label="100" alpha="255"/>
          <item color="#000000" value="10000" label="10000" alpha="255"/>
          <rampLegendSettings suffix="" orientation="2" maximumLabel="" minimumLabel="" useContinuousLegend="1" direction="0" prefix="">
            <numericFormat id="basic">
              <Option type="Map">
                <Option value="" name="decimal_separator" type="QChar"/>
                <Option value="6" name="decimals" type="int"/>
                <Option value="0" name="rounding_type" type="int"/>
                <Option value="false" name="show_plus" type="bool"/>
                <Option value="true" name="show_thousand_separator" type="bool"/>
                <Option value="false" name="show_trailing_zeros" type="bool"/>
                <Option value="" name="thousand_separator" type="QChar"/>
              </Option>
            </numericFormat>
          </rampLegendSettings>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast gamma="1" contrast="0" brightness="0"/>
    <huesaturation saturation="0" colorizeGreen="128" colorizeStrength="100" colorizeOn="0" colorizeRed="255" invertColors="0" colorizeBlue="128" grayscaleMode="0"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
