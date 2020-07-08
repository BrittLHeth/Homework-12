const url = "http://robdunnlab.com/projects/belly-button-biodiversity/";

// Fetch the JSON data and console log it
d3.json(url).then(function(data) {
  console.log(data);
});

