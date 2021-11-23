// Call the dataTables jQuery plugin
$(document).ready(function() {
  $('#dataTable-positive').DataTable({
    "scrollY": "200px",
  });

  $('#dataTable-negative').DataTable({
    "scrollY": "200px",
  });

  $('#dataTable-neutral').DataTable({
    "scrollY": "200px",
  });
});
