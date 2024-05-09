var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
  return new bootstrap.Popover(popoverTriggerEl)
})

$(document).ready(function(){

  $('.toggle-btn').click(function() {
  $(this).toggleClass('active').siblings().removeClass('active');
  });
  
  });