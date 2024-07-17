//

// const { renderAirplane } = require("./airplane");

console.log("Hello, world!")

// RENDERING OF CESIUM ION CONTAINER in GLOBE page. 
const viewer = new Cesium.Viewer("cesiumContainer", {
  baseLayer: false,
  baseLayerPicker: false,
  infoBox: false,
  requestRenderMode: true, // render only when needed
});

viewer.scene.debugShowFramesPerSecond = true;

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
// init black marble layer and await its loading in an async function.
let blackMarbleLayer = null;  // Initialize the layer variable but do not load until needed.

async function ensureBlackMarbleLayer() {
    if (!blackMarbleLayer) {  // Only load if not already loaded.
        blackMarbleLayer = await Cesium.ImageryLayer.fromProviderAsync(
            Cesium.IonImageryProvider.fromAssetId(3812)
        );

    //lighten dark mode slightly so bing maps overlay is visible?
    blackMarbleLayer.brightness = 3.0; // > 1.0 increases brightness.  < 1.0 decreases
    blackMarbleLayer.alpha = 0.75;
 
    }
}

document.getElementById('dayNightToggle').addEventListener('change', async function () {
    const label = document.getElementById('toggleLabel');
    await ensureBlackMarbleLayer();  // verifies layer is loaded before toggling.

    if (this.checked) {
        viewer.scene.skyAtmosphere.hueShift = -0.8;
        viewer.scene.skyAtmosphere.saturationShift = -0.7;
        viewer.scene.skyAtmosphere.brightnessShift = -0.33;
        viewer.scene.globe.enableLighting = false;
        label.innerText = 'Night Mode';

        // Add the black marble layer for night mode.
        viewer.imageryLayers.add(blackMarbleLayer);
    } else {
        viewer.scene.skyAtmosphere.hueShift = 0.0;
        viewer.scene.skyAtmosphere.saturationShift = 0.0;
        viewer.scene.skyAtmosphere.brightnessShift = 0.0;
        viewer.scene.globe.enableLighting = false;
        label.innerText = 'Day Mode';

        // Remove the black marble layer if previously added.
        viewer.imageryLayers.remove(blackMarbleLayer, true);  // Use true for destroy to properly clean up.
        blackMarbleLayer = null;  // Reset the layer variable.
    }
});








// INSTURCTION WINDOW
const instructionWindow = document.createElement('div');
instructionWindow.id = 'instructionWindow';

// Create the content container
const contentContainer = document.createElement('div');
contentContainer.innerHTML = `
  <h2>geoleek Simulation Sandbox</h2> 
  <h3>Instructions:</h3> <br/>
  <p>1. Using the scroll wheel on the mouse, zoom in & zoom out on the globe. To reposition to a different region, you may also click and drag.</p>
  <p>2. To begin the simulation, please place 4 receivers by right clicking. Please note the receivers need to be placed within a 500km of one another.</p>
  <p>3. Double-click or use the 'Render Airplane' button and click to place an airplane withing 500km of the placed receivers. 
        Please note, a minimum of 4 receivers must be placed before an airplane can be populated. </p>
`;

// Style the instruction window
instructionWindow.style.cssText = `
  position: absolute;
  top: 150px;
  left: 10px;
  background-color: rgba(255, 255, 255, 0.7);
  color: black;
  border-radius: 5px;
  padding: 10px;
  font-family: Times New Roman;
  font-size: 20px;
  z-index: 1000;
  max-width: 450px;
  transition: all 0.3s ease;
`;

// Create the toggle button
const toggleButton = document.createElement('button');
toggleButton.innerHTML = '−'; // Unicode minus sign
toggleButton.style.cssText = `
  position: absolute;
  top: 5px;
  right: 5px;
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
`;

let isMinimized = false;

function toggleInstructions() {
  if (isMinimized) {
    // Expanding the simulation instructions window - style guidelines
    contentContainer.style.display = 'block';
    instructionWindow.style.cssText = `
      position: absolute;
      top: 150px;
      left: 10px;
      background-color: rgba(255, 255, 255, 0.7);
      color: black;
      border-radius: 5px;
      padding: 10px;
      font-family: Times New Roman;
      font-size: 20px;
      z-index: 1000;
      max-width: 450px;
      transition: all 0.3s ease;
      height: auto;
      width: auto;
      display: block;
    `;
    toggleButton.style.cssText = `
      position: absolute;
      top: 5px;
      right: 5px;
      background: none;
      border: none;
      font-size: 28px;
      cursor: pointer;
      color: black;
    `;
    toggleButton.innerHTML = '−';
  } else {
    // Minimizing the simulation instruction window
    contentContainer.style.display = 'none';
    instructionWindow.style.cssText = `
      position: absolute;
      top: 150px;
      left: 10px;
      background-color: rgba(0, 0, 0, 0.7);
      color: white;
      border-radius: 50%;
      padding: 0;
      font-family: Times New Roman;
      font-size: 20px;
      z-index: 1000;
      height: 40px;
      width: 40px;
      display: flex;
      justify-content: center;
      align-items: center;
      transition: all 0.3s ease;
    `;
    toggleButton.style.cssText = `
      position: static;
      background: none;
      border: none;
      font-size: 24px;
      cursor: pointer;
      color: white;
      line-height: 1;
    `;
    toggleButton.innerHTML = '+';
  }
  isMinimized = !isMinimized;
}


toggleButton.onclick = toggleInstructions;

// Assemble the instruction window
instructionWindow.appendChild(contentContainer);
instructionWindow.appendChild(toggleButton);

// Add the instruction window to the DOM
document.getElementById('cesiumContainer').appendChild(instructionWindow);





//TODO
//MOUSE COORDINATES TRACKER
// let viewer = new Cesium.Viewer('cesiumContainer');

// // Add event handler for mouse move to display coordinates
// viewer.screenSpaceEventHandler.setInputAction(function(movement) {
//     var cartesian = viewer.camera.pickEllipsoid(movement.endPosition, viewer.scene.globe.ellipsoid);
//     if (cartesian) {
//         var cartographic = Cesium.Cartographic.fromCartesian(cartesian);
//         var longitudeString = Cesium.Math.toDegrees(cartographic.longitude).toFixed(5);
//         var latitudeString = Cesium.Math.toDegrees(cartographic.latitude).toFixed(5);
//         document.getElementById('latitudeValue').textContent = latitudeString;
//         document.getElementById('longitudeValue').textContent = longitudeString;
//     }
// }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);







// BUTTON & DOUBLE LEFT CLICK TO ADD AIRCRAFT (emitter) once 4 collectors have been placed
  const airplaneButton = document.createElement('button');





function getElevation(latitude, longitude) {
  // Return the fetch promise directly
  return fetch('/get-elevation', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({latitude: latitude, longitude: longitude})
  })
  .then(response => response.json())
  .then(data => {
      console.log('Elevation:', data.elevation); // Logging the elevation for debugging
      return data.elevation; // Return elevation so it can be awaited on
  })
  .catch(error => {
      console.error('Error fetching elevation:', error);
      return undefined; // Return undefined or throw an error as you see fit
  });
}

const receivers = [];

// USER INTERACTIVITY TO DROP POINTS ON MAP (THIS IS DONE BY RIGHT CLICKING)
//bettereer as a function for implementation purposes? 
function placeScalingReceivers(viewer) {
  let pointCount = 0;
  const minPoints = 4; // 4 points need to be placed
  const maxDistance = 500000; // 500 km in meters
  let lastPoint = null;

  viewer.screenSpaceEventHandler.setInputAction(async (click) => {  // Make this function async
    const cartesian = viewer.scene.pickPosition(click.position);
    if (Cesium.defined(cartesian) && pointCount < minPoints) {
      if (lastPoint && Cesium.Cartesian3.distance(lastPoint, cartesian) > maxDistance) {
        alert("Points must be within 500km of each to each other. Please try again.");
        return;
      }

      const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
      const lon = Cesium.Math.toDegrees(cartographic.longitude);
      const lat = Cesium.Math.toDegrees(cartographic.latitude);
      
      try {
          const elevation = await getElevation(lat, lon);  // Await the elevation from the API
          receivers.push({
              latitude: lat,
              longitude: lon,
              altitude: elevation  // Use the actual elevation
          });

          console.log('Receiver Added:', {latitude: lat, longitude: lon, altitude: elevation});
          console.log('All Receivers:', receivers);  // Optional: log the current state of the receivers array
          
          viewer.entities.add({
            position: cartesian,
            billboard: {
                image: 'static/images/marker.png',
                width: 32,
                height: 40,
                verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
            }
          });

          lastPoint = cartesian;
          pointCount++;
          if (pointCount >= minPoints) {
            airplaneButton.disabled = false;
          }
      } catch (error) {
          console.error('Error fetching elevation:', error);
      }
    }
  }, Cesium.ScreenSpaceEventType.RIGHT_CLICK);
}

placeScalingReceivers(viewer);










//AIRPLANE MODEL CODE
// CREATION OF 3-D AIRCRAFT MODEL
function createModel(url, height, longitude, latitude) {
  // viewer.entities.removeAll(); //removes receivers when airplane is placed

  const position = Cesium.Cartesian3.fromDegrees(
    longitude,
    latitude,
    height
  );

  const heading = Cesium.Math.toRadians(135);
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
      uri: "static/models/cirrus_sr22.glb",
      minimumPixelSize: 128,
      maximumScale: 20000,
    },
  });

  // viewer.trackedEntity = entity; // zooms in on airplane model when placed

  return entity;
}

function createLabel(longitude, latitude, height, labelText) {
  const position = Cesium.Cartesian3.fromDegrees(longitude, latitude, height + 50); // Adjust height to place the label above the plane
  
  const labelEntity = viewer.entities.add({
    position: position,
    label: {
      text: labelText,
      font: '14pt monospace',
      fillColor: Cesium.Color.WHITE,
      outlineColor: Cesium.Color.BLACK,
      outlineWidth: 2,
      style: Cesium.LabelStyle.FILL_AND_OUTLINE,
      verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
      pixelOffset: new Cesium.Cartesian2(0, -50) // Pixel offset to adjust label's vertical position
    }
  });

  return labelEntity;
}

// Export the createModel function if needed
// (This is optional and depends on your project structure)
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
  module.exports = {
    createModel: createModel

  };
}



// RENDER AIRPLANE BUTTON
let emitterButton; // moved outside of function because bug otherwise

function initializeEmitterControls(emitter) {

  if (!emitterButton) {
    emitterButton = document.createElement('button');
    emitterButton.id = 'renderEmitterButton';
    emitterButton.textContent = 'Render Aircraft'; // button text when globe renders

    // Styling for the button
    emitterButton.style.backgroundColor = '#8e8ebd';
    emitterButton.style.border = 'none';
    emitterButton.style.color = 'white';
    emitterButton.style.padding = '10px 30px';
    emitterButton.style.textAlign = 'center';
    emitterButton.style.textDecoration = 'none';
    emitterButton.style.display = 'inline-block';
    emitterButton.style.fontSize = '21px';
    emitterButton.style.fontFamily = 'Times New Roman';
    emitterButton.style.margin = '4px 2px';
    emitterButton.style.cursor = 'pointer';
    emitterButton.style.borderRadius = '4px';

    // Hover effect for button
    emitterButton.addEventListener('mouseover', function() {
      this.style.backgroundColor = '#8e8ebd';
    });
    emitterButton.addEventListener('mouseout', function() {
      this.style.backgroundColor = '#474772';
    });

    // Add button to desired location (e.g., Cesium toolbar)
    const toolbar = document.querySelector('.cesium-viewer-toolbar');
    toolbar.insertBefore(emitterButton, toolbar.firstChild);
  }

  // Setup click event listener to start placement process
  emitterButton.addEventListener('click', () => {
    // Change button text and behavior upon click
    emitterButton.textContent = 'Click on the globe to place an Aircraft';
    // emitterButton.disabled = true;

    // Change cursor style to crosshair to indicate placement mode
    viewer.scene.canvas.style.cursor = 'crosshair';

    // Set up click action on the globe to place the aircraft
    viewer.screenSpaceEventHandler.setInputAction((click) => {
      const earthPosition = viewer.scene.pickPosition(click.position);
      if (Cesium.defined(earthPosition)) {
        const cartographic = Cesium.Cartographic.fromCartesian(earthPosition);
        const longitude = Cesium.Math.toDegrees(cartographic.longitude);
        const latitude = Cesium.Math.toDegrees(cartographic.latitude);

        // Prompt user for altitude
        // let altitudeStr = window.prompt('Enter altitude (meters):');
        // let altitude = parseFloat(altitudeStr);
        // if (isNaN(altitude)) {
        //   alert('Invalid input. Please enter a valid number for altitude.');
        //   return;
        // }
        let inputs = [];
        let messages = [
          'Enter altitude (meters MSL):',
          'Enter north velocity (meters/second):',
          'Enter east velocity (meters/second):'
        ];

        for (let i = 0; i < messages.length; i++) {
          inputs.push(window.prompt(messages[i]));
        }

        // Parse input strings to floats
        let altitude = parseFloat(inputs[0]);
        let northVelocity = parseFloat(inputs[1]);
        let eastVelocity = parseFloat(inputs[2]);

        let emitterInfo = {
          latitude: latitude,
          longitude: longitude,
          altitude: altitude,
          northVelocity: northVelocity,
          eastVelocity: eastVelocity
        };

        console.log("Emitter added:", emitterInfo);

        // Check if inputs are valid numbers
        if (!isNaN(altitude) && !isNaN(northVelocity) && !isNaN(eastVelocity)) {
          // Process altitude, northVelocity, and eastVelocity here
          console.log('Altitude:', altitude);
          console.log('North Velocity:', northVelocity);
          console.log('East Velocity:', eastVelocity);

          // You can perform further calculations or processing with these values
        } else {
          alert('Invalid input. Please enter valid numbers for altitude, north velocity, and east velocity.');
        }

        // Create the model entity (replace with your createModel function)
        const entity = createModel(
          "static/models/cirrus_sr22.glb",
          altitude,
          longitude,
          latitude
        );

        
        // Reset cursor style and button text after placement
        viewer.scene.canvas.style.cursor = 'default';
        emitterButton.textContent = 'Render Aircraft';
        // emitterButton.disabled = false;
        runSimulation(emitterInfo);
      }
    }, 
    
    Cesium.ScreenSpaceEventType.LEFT_CLICK);
    viewer.scene.canvas.style.cursor = 'default';
    emitterButton.textContent = 'Render Aircraft';
    

  });
}



function runSimulation(emitterInfo) {
  console.log("Running simulation...")
  fetch('/run-simulation', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({
          emitter: emitterInfo,
          receivers: receivers
      })
  })
  .then(response => response.json())
  .then(data => {
      console.log('Simulation result:', data);
      // Extract the estimated position and other data from the response
      const cafEmitterPos = data.caf_emitter;
      const caf_latitude =  cafEmitterPos.latitude;
      const caf_longitude = cafEmitterPos.longitude;
      const caf_altitude =  cafEmitterPos.altitude;

      const estEmitterPos = data.true_emitter;
      const est_latitude = estEmitterPos.latitude;
      const est_longitude = estEmitterPos.longitude;
      const est_altitude = estEmitterPos.altitude;
      
      // Optionally, handle position and velocity errors
      // const posError = data.posError;
      // const velError = data.velError;
      // console.log('Position Error:', posError);
      // console.log('Velocity Error:', velError);

      // Plot the aircraft model using the returned estimated position
      const cafModelEntity = createModel(
          "static/models/cirrus_sr22.glb",
          caf_altitude,
          caf_longitude,
          caf_latitude
      );

      const cafTextEntity = createLabel(caf_longitude, caf_latitude, caf_altitude, 'Estimated Position with CAF');

      const estModelEntity = createModel(
        "static/models/cirrus_sr22.glb",
        est_altitude,
        est_longitude,
        est_latitude
    );

    const estTextEntity = createLabel(est_longitude, est_latitude, est_altitude, 'Estimated Position with True T/FDOA Data');

  })
  .catch(error => console.error('Error during simulation or plotting:', error));
}


// Call this function after the page has loaded and viewer is initialized
document.addEventListener('DOMContentLoaded', () => { // DOM = Document Object Model
  setupEmitterControls();
});

function setupEmitterControls() { //function call
  initializeEmitterControls(viewer); // view is defined at beginning
}

// createModel(
//   "static/models/cirrus_sr22.glb",
//   200,   // height
//   -104.0,   // longitude
//   39.0  // latitude
// );