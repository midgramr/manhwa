const myInput = document.getElementById('onOffToggle');
myInput.addEventListener('input', (event) => {
  // put netowkr call here with event.target.value
  console.log(event.target.value)
});