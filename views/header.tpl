<html>
<head>
    <title>ADB{{title}}</title>
    <link rel="stylesheet" type="text/css" href="static/bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="static/theme.css">
    <link rel="stylesheet" type="text/css" href="static/examples.css">
    <script type="text/javascript" src="static/jquery.js"></script>
    <script type="text/javascript" src="static/extra.js"></script>
    <script type="text/javascript" src="static/typeahead.min.js"></script>
    <script type="text/javascript" src="static/bootstrap.min.js"></script>

    <script type="text/javascript" src="static/jdpicker.js"></script>
	<script>
	  $( document ).ready(function() {
            $('#typeahead').typeahead({
                name: 'answerLines',
                prefetch: '/static/answerLines_HS.json',
                limit: 5
            });
        });
	</script>
    <link rel="stylesheet" type="text/css" href="static/jdpicker.css">
    <link rel="icon" type="image/png" href="static/recoll.png">
</head>
<body>
<div id="fade"></div>
