$(document).ready(function() {
    var todaysDate = new Date();
    var day = [];
    day[0] = "sun";
    day[1] = "mon";
    day[2] = "tue";
    day[3] = "wed";
    day[4] = "thu";
    day[5] = "fri";
    day[6] = "sat";
  
    var currentDay = day[todaysDate.getDay()];
  
    var currentDayID = "#" + currentDay;
    $(currentDayID).toggleClass("today");
  });