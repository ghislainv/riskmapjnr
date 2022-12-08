<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="AllStyleCategories" minScale="1e+08" version="3.22.12-Białowieża" maxScale="0" hasScaleBasedVisibilityFlag="0">
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
      <Option name="WMSBackgroundLayer" type="QString" value="false"/>
      <Option name="WMSPublishDataSourceUrl" type="QString" value="false"/>
      <Option name="embeddedWidgets/count" type="QString" value="0"/>
      <Option name="identify/format" type="QString" value="Value"/>
    </Option>
  </customproperties>
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option name="name" type="QString" value=""/>
      <Option name="properties"/>
      <Option name="type" type="QString" value="collection"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling enabled="false" zoomedInResamplingMethod="nearestNeighbour" zoomedOutResamplingMethod="nearestNeighbour" maxOversampling="2"/>
    </provider>
    <rasterrenderer alphaBand="-1" classificationMin="0" classificationMax="10000" band="1" type="singlebandpseudocolor" opacity="1" nodataColor="">
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
        <colorrampshader colorRampType="INTERPOLATED" clip="0" classificationMode="1" maximumValue="10000" minimumValue="0" labelPrecision="0">
          <colorramp name="[source]" type="gradient">
            <Option type="Map">
              <Option name="color1" type="QString" value="34,139,34,255"/>
              <Option name="color2" type="QString" value="0,0,0,255"/>
              <Option name="discrete" type="QString" value="0"/>
              <Option name="rampType" type="QString" value="gradient"/>
              <Option name="stops" type="QString" value="0.005;255,165,0,255:0.01;215,25,28,255"/>
            </Option>
            <prop k="color1" v="34,139,34,255"/>
            <prop k="color2" v="0,0,0,255"/>
            <prop k="discrete" v="0"/>
            <prop k="rampType" v="gradient"/>
            <prop k="stops" v="0.005;255,165,0,255:0.01;215,25,28,255"/>
          </colorramp>
          <item alpha="255" label="0" color="#228b22" value="0"/>
          <item alpha="255" label="50" color="#ffa500" value="50"/>
          <item alpha="255" label="100" color="#d7191c" value="100"/>
          <item alpha="255" label="10000" color="#000000" value="10000"/>
          <rampLegendSettings minimumLabel="" direction="0" orientation="2" maximumLabel="" prefix="" suffix="" useContinuousLegend="1">
            <numericFormat id="basic">
              <Option type="Map">
                <Option name="decimal_separator" type="QChar" value=""/>
                <Option name="decimals" type="int" value="6"/>
                <Option name="rounding_type" type="int" value="0"/>
                <Option name="show_plus" type="bool" value="false"/>
                <Option name="show_thousand_separator" type="bool" value="true"/>
                <Option name="show_trailing_zeros" type="bool" value="false"/>
                <Option name="thousand_separator" type="QChar" value=""/>
              </Option>
            </numericFormat>
          </rampLegendSettings>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" gamma="1" contrast="0"/>
    <huesaturation saturation="0" colorizeGreen="128" colorizeRed="255" colorizeBlue="128" colorizeStrength="100" colorizeOn="0" invertColors="0" grayscaleMode="0"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
