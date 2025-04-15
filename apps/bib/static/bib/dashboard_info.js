document.addEventListener("DOMContentLoaded", function() {
  fetch(dashboard_info_link)
    .then(response => response.json())
    .then(data => {
      const newItems = document.querySelector('div#new-items');
      const updates = document.querySelector('div#updates');
      newItems.innerHTML = data.new_items;
      updates.innerHTML = data.updates;
    })
  })
