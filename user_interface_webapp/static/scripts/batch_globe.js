
// RENDERING OF CESIUM ION CONTAINER in GLOBE page.
const viewer = new Cesium.Viewer("cesiumContainer", {
    baseLayerPicker: false,
    infoBox: false,
  });
  
  const layers = viewer.imageryLayers;
  
  // Add Bing Maps Aerial with Labels to the left panel
  const bingMapsAerialWithLabels = Cesium.ImageryLayer.fromProviderAsync(
    Cesium.IonImageryProvider.fromAssetId(3)
  );
  bingMapsAerialWithLabels.splitDirection = Cesium.SplitDirection.LEFT;
  layers.add(bingMapsAerialWithLabels);
  
  // Add Bing Maps Aerial (unlabeled) to the right panel
  const bingMapsAerial = Cesium.ImageryLayer.fromProviderAsync(
    Cesium.IonImageryProvider.fromAssetId(2)
  );
  bingMapsAerial.splitDirection = Cesium.SplitDirection.RIGHT;
  layers.add(bingMapsAerial);
  
  // Add high resolution Washington DC imagery to both panels.
  const imageryLayer = Cesium.ImageryLayer.fromProviderAsync(
    Cesium.IonImageryProvider.fromAssetId(3827)
  );
  viewer.imageryLayers.add(imageryLayer);
  
  // Add Bing Maps Labels Only to the right panel
  const bingMapsLabelsOnly = Cesium.ImageryLayer.fromProviderAsync(
    Cesium.IonImageryProvider.fromAssetId(2411391)
  );
  bingMapsLabelsOnly.splitDirection = Cesium.SplitDirection.RIGHT; // Only show to the left of the slider.
  layers.add(bingMapsLabelsOnly);
  
  // DARK MODE IMPLEMENTATION - note that the map renders in night mode but the city & road features are no longer visible.
  let blackMarbleLayer = null; // Initialize the layer variable but do not load until needed.
  
  async function ensureBlackMarbleLayer() {
    if (!blackMarbleLayer) {
      // Only load if not already loaded.
      blackMarbleLayer = await Cesium.ImageryLayer.fromProviderAsync(
        Cesium.IonImageryProvider.fromAssetId(3812)
      );
    }
  }
  
  document
    .getElementById("dayNightToggle")
    .addEventListener("change", async function () {
      const label = document.getElementById("toggleLabel");
      await ensureBlackMarbleLayer(); // Ensure layer is loaded before toggling.
  
      if (this.checked) {
        viewer.scene.skyAtmosphere.hueShift = -0.8;
        viewer.scene.skyAtmosphere.saturationShift = -0.7;
        viewer.scene.skyAtmosphere.brightnessShift = -0.33;
        viewer.scene.globe.enableLighting = false;
        label.innerText = "Night Mode";
  
        // Add the black marble layer for night mode.
        viewer.imageryLayers.add(blackMarbleLayer);
      } else {
        viewer.scene.skyAtmosphere.hueShift = 0.0;
        viewer.scene.skyAtmosphere.saturationShift = 0.0;
        viewer.scene.skyAtmosphere.brightnessShift = 0.0;
        viewer.scene.globe.enableLighting = false;
        label.innerText = "Day Mode";
  
        // Remove the black marble layer if previously added.
        viewer.imageryLayers.remove(blackMarbleLayer, true); // Use `true` for destroy to properly clean up.
        blackMarbleLayer = null; // Reset the layer variable.
      }
    });
  
  function calculateHeading(previousPosition, currentPosition) {
    // Use Cesium's API to calculate the surface distance and initial heading
    const startCartographic = Cesium.Cartographic.fromCartesian(previousPosition);
    const endCartographic = Cesium.Cartographic.fromCartesian(currentPosition);
    const ellipsoidGeodesic = new Cesium.EllipsoidGeodesic(startCartographic, endCartographic);
  
    // Return the initial heading in radians
    return ellipsoidGeodesic.startHeading;
  }

  // This function uses embedded flight data to plot points
  function addFlightDataToGlobe() {
    if (typeof flightData === "string") {
      flightData = JSON.parse(flightData);
    }
  
    // Group data by TIME to synchronize all flight updates
    const groupedByTime = groupBy(flightData, "TIME");
    const timestamps = Object.keys(groupedByTime).sort((a, b) => a - b);
  
    let currentTimestampIndex = 0;
    let flightEntities = {};
  
    function updateEntities() {
      const currentTime = timestamps[currentTimestampIndex];
      const flightsAtCurrentTime = groupedByTime[currentTime];
  
      flightsAtCurrentTime.forEach((flight) => {
        const icao = flight.ICAO;
        const position = Cesium.Cartesian3.fromDegrees(
          parseFloat(flight.LON),
          parseFloat(flight.LAT)
        );
  
        if (!flightEntities[icao]) {
          // First occurrence of this ICAO; create new entities
          flightEntities[icao] = {
            positions: [position],
            polyline: viewer.entities.add({
              polyline: {
                positions: new Cesium.CallbackProperty(
                  () => flightEntities[icao].positions,
                  false
                ),
                width: 3,
                material: Cesium.Color.MAGENTA.withAlpha(0.75),
              },
            }),
            model: createModel(
              "static/models/cirrus_sr22.glb",
              1000,
              parseFloat(flight.LON),
              parseFloat(flight.LAT),
              0
            ),
            label: viewer.entities.add({
              position: position,
              label: {
                text: `ICAO: ${icao}`,
                font: "14pt monospace",
                style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                outlineWidth: 2,
                verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                pixelOffset: new Cesium.Cartesian2(15, -35),
                fillColor: Cesium.Color.YELLOW, 
              },
            }),
            lastHeading: null
          };
        } else {
          const previousPosition = flightEntities[icao].positions[flightEntities[icao].positions.length - 1];
          const currentPosition = position;
          if (!Cesium.Cartesian3.equals(previousPosition, currentPosition)) {
            const heading = calculateHeading(previousPosition, currentPosition) * 360 / (2 * Math.PI) ;
            // Updates existing polyline, model, and label
            console.log(heading, flightEntities[icao].lastHeading)
            if (flightEntities[icao].lastHeading !== null && Math.abs(heading - flightEntities[icao].lastHeading) < 90) {
              if (icao === 'a121c0'){
                console.log(icao, previousPosition, currentPosition, heading)
              }
              flightEntities[icao].positions.push(position);
              flightEntities[icao].model.position = position;
              flightEntities[icao].label.position = position;
              flightEntities[icao].model.orientation = Cesium.Transforms.headingPitchRollQuaternion(
                currentPosition,
                new Cesium.HeadingPitchRoll(Cesium.Math.toRadians(heading), 0, 0)
              );
              flightEntities[icao].label.label.text = `ICAO: ${icao}`;
              flightEntities[icao].lastHeading = heading;
            }
            else if (flightEntities[icao].lastHeading === null) {
              flightEntities[icao].positions.push(position);
              flightEntities[icao].model.position = position;
              flightEntities[icao].label.position = position;
              flightEntities[icao].model.orientation = Cesium.Transforms.headingPitchRollQuaternion(
                currentPosition,
                new Cesium.HeadingPitchRoll(Cesium.Math.toRadians(heading), 0, 0)
              );
              flightEntities[icao].label.label.text = `ICAO: ${icao}`;
              flightEntities[icao].lastHeading = heading;
            }

          }

          }
      });
  
      currentTimestampIndex++;
      if (currentTimestampIndex >= timestamps.length) {
        currentTimestampIndex = 0; // set to 0 for looping
        Object.keys(flightEntities).forEach((icao) => {
          flightEntities[icao].positions = [];
        });
      }
      setTimeout(updateEntities, 1000); // Adjust timing as necessary
    }
  
    updateEntities(); // Start the update process
  }
  
  function createModel(url, height, longitude, latitude, heading) {
    const position = Cesium.Cartesian3.fromDegrees(
      longitude,
      latitude,
      height
    );
    const pitch = 0;
    const roll = 0;
    const hpr = new Cesium.HeadingPitchRoll(heading, pitch, roll);
    const orientation = Cesium.Transforms.headingPitchRollQuaternion(
      position,
      hpr
    );
  
    const entity = viewer.entities.add({
      name: url,
      position: position,
      orientation: orientation,
      model: {
        uri: url,
        minimumPixelSize: 128,
        maximumScale: 20000,
      },
    });
  
    return entity;
  }
  
  // Helper function to group by a key
  function groupBy(array, key) {
    return array.reduce((result, currentValue) => {
      (result[currentValue[key]] = result[currentValue[key]] || []).push(
        currentValue
      );
      return result;
    }, {});
  }
  
  // Call the function to add data to the globe as part of the page loading process
  document.addEventListener("DOMContentLoaded", addFlightDataToGlobe);
  