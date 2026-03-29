const myInput = document.getElementById('onOffToggle');
myInput.addEventListener('input', (event) => {
  window.toggle = !window.toggle;
  window.postMessage({
  type: "TOGGLE_UPDATE",
  toggle: window.toggle
}, "*");
});