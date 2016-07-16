$(document).ready(function() {
	$("tr").mouseover(function() {
		$(this).addClass("over");
	});

	$("tr").mouseout(function() {
		$(this).removeClass("over");
	});
	
	$("#theTable").tablesorter({
		sortList:[[1,0]],
		cssAsc: "sortUp",
		cssDesc: "sortDown",
		widgets: ["zebra"]
	});
});
