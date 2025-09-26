fetch('/api/send-sos', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ lat: 19.076, lon: 72.877 }) // example
})
.then(res => res.json())
.then(data => {
  console.log("Response:", data);
})
.catch(err => {
  console.error("Error parsing JSON:", err);
});
