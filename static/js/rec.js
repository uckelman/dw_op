var rec = document.getElementById('recommendation');

rec.addEventListener("input", function(event) {
  rec.setCustomValidity(rec.value.length > 4096 ? "Too much!" : "");
});

