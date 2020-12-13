$(document).ready(function(){
	$("form").submit(function() {
		$("input").blur()
		$("#fade").height($("#searchbox").height()+1)
		$("#fade").fadeIn("slow")
	})
	if ($("#results").length) { $("input").blur() }
});

$( document ).ready(function() {
    $('#typeahead').typeahead({
	name: 'answerLines',
	prefetch: '/static/answerLines_HS.json',
	limit: 5
    });
});
