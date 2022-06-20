<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="0" minScale="1e+08" styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="0" version="3.22.7-Białowieża">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal mode="0" fetchMode="0" enabled="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option type="QString" value="false" name="WMSBackgroundLayer"/>
      <Option type="QString" value="false" name="WMSPublishDataSourceUrl"/>
      <Option type="QString" value="0" name="embeddedWidgets/count"/>
      <Option type="QString" value="Value" name="identify/format"/>
    </Option>
  </customproperties>
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option type="QString" value="" name="name"/>
      <Option name="properties"/>
      <Option type="QString" value="collection" name="type"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling zoomedOutResamplingMethod="nearestNeighbour" enabled="false" zoomedInResamplingMethod="nearestNeighbour" maxOversampling="2"/>
    </provider>
    <rasterrenderer classificationMax="30" nodataColor="" type="singlebandpseudocolor" band="1" alphaBand="-1" opacity="1" classificationMin="0">
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
        <colorrampshader minimumValue="0" maximumValue="30" classificationMode="2" labelPrecision="0" clip="0" colorRampType="EXACT">
          <colorramp type="gradient" name="[source]">
            <Option type="Map">
              <Option type="QString" value="34,139,34,255" name="color1"/>
              <Option type="QString" value="0,0,0,255" name="color2"/>
              <Option type="QString" value="0" name="discrete"/>
              <Option type="QString" value="gradient" name="rampType"/>
              <Option type="QString" value="0.0333333;255,165,0,255:0.5;215,25,28,255" name="stops"/>
            </Option>
            <prop k="color1" v="34,139,34,255"/>
            <prop k="color2" v="0,0,0,255"/>
            <prop k="discrete" v="0"/>
            <prop k="rampType" v="gradient"/>
            <prop k="stops" v="0.0333333;255,165,0,255:0.5;215,25,28,255"/>
          </colorramp>
          <item alpha="255" color="#228b22" label="0" value="0"/>
          <item alpha="255" color="#ffa500" label="1" value="1"/>
          <item alpha="255" color="#fc9b02" label="2" value="2"/>
          <item alpha="255" color="#f99104" label="3" value="3"/>
          <item alpha="255" color="#f68706" label="4" value="4"/>
          <item alpha="255" color="#f47d08" label="5" value="5"/>
          <item alpha="255" color="#f1730a" label="6" value="6"/>
          <item alpha="255" color="#ee690c" label="7" value="7"/>
          <item alpha="255" color="#eb5f0e" label="8" value="8"/>
          <item alpha="255" color="#e85510" label="9" value="9"/>
          <item alpha="255" color="#e54b12" label="10" value="10"/>
          <item alpha="255" color="#e24114" label="11" value="11"/>
          <item alpha="255" color="#e03716" label="12" value="12"/>
          <item alpha="255" color="#dd2d18" label="13" value="13"/>
          <item alpha="255" color="#da231a" label="14" value="14"/>
          <item alpha="255" color="#d7191c" label="15" value="15"/>
          <item alpha="255" color="#c9171a" label="16" value="16"/>
          <item alpha="255" color="#ba1618" label="17" value="17"/>
          <item alpha="255" color="#ac1416" label="18" value="18"/>
          <item alpha="255" color="#9e1215" label="19" value="19"/>
          <item alpha="255" color="#8f1113" label="20" value="20"/>
          <item alpha="255" color="#810f11" label="21" value="21"/>
          <item alpha="255" color="#730d0f" label="22" value="22"/>
          <item alpha="255" color="#640c0d" label="23" value="23"/>
          <item alpha="255" color="#560a0b" label="24" value="24"/>
          <item alpha="255" color="#480809" label="25" value="25"/>
          <item alpha="255" color="#390707" label="26" value="26"/>
          <item alpha="255" color="#2b0506" label="27" value="27"/>
          <item alpha="255" color="#1d0304" label="28" value="28"/>
          <item alpha="255" color="#0e0202" label="29" value="29"/>
          <item alpha="255" color="#000000" label="30" value="30"/>
          <rampLegendSettings minimumLabel="" useContinuousLegend="1" maximumLabel="" direction="0" prefix="" orientation="2" suffix="">
            <numericFormat id="basic">
              <Option type="Map">
                <Option type="QChar" value="" name="decimal_separator"/>
                <Option type="int" value="6" name="decimals"/>
                <Option type="int" value="0" name="rounding_type"/>
                <Option type="bool" value="false" name="show_plus"/>
                <Option type="bool" value="true" name="show_thousand_separator"/>
                <Option type="bool" value="false" name="show_trailing_zeros"/>
                <Option type="QChar" value="" name="thousand_separator"/>
              </Option>
            </numericFormat>
          </rampLegendSettings>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast gamma="1" brightness="0" contrast="0"/>
    <huesaturation colorizeOn="0" colorizeStrength="100" colorizeGreen="128" invertColors="0" colorizeBlue="128" saturation="0" colorizeRed="255" grayscaleMode="0"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
