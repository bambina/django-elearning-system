// This script is used to update the date and time of the ended QA session
document.addEventListener("DOMContentLoaded", function () {
  function updateAllDateTimes() {
    const elements = document.getElementsByClassName("utc-timestamp");
    for (let element of elements) {
      const timestamp = element.getAttribute("data-timestamp");
      var options = {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      };
      element.textContent = `Posted on ${new Date(timestamp).toLocaleTimeString(
        [],
        options
      )}`;
    }
  }

  updateAllDateTimes();
});
