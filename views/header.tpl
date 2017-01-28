<html>
<head>
    <title>aseemsDB{{title}}</title>
    <link rel="stylesheet" type="text/css" href="static/bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="static/examples.css">
    <link rel="stylesheet" type="text/css" href="static/style.css">
    <link rel="stylesheet" type="text/css" href="static/theme.css">
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
    <link rel="search" type="application/opensearchdescription+xml" title="recoll" href="osd.xml">
</head>
<body>
<div id="fade"></div>
