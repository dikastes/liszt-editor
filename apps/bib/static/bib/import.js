let bulkCount = bulks.length;
const bulkSize = bulks.length / count;
const stepSize = 100 / bulkCount;
let progress = 0;

const calcRadialStyle = x => `--value:${Math.ceil(x)}; --size:12rem; --thickness: 2rem;`;
const calcCountStyle = x => `--value:${Math.ceil(x)};`;

function conditionalRedirect() {
  progress += stepSize;
  progressBar = document.querySelector('progress.progress');
  progressBar.value = Math.ceil(progress);

  bulkCount--;
  if (bulkCount == 0) {
    location = dashboardUrl;
  }
}

function handleBulkDiv(link) {
  fetch(link).then( function() {
    conditionalRedirect();
  })
}

document.addEventListener("DOMContentLoaded", function() {
  bulks.forEach( function(link) { handleBulkDiv(link); });
})
