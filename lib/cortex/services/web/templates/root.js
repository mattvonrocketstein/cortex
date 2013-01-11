jQuery(document).ready(function(){
    $('#id_graph').load('/static/graph_cortex.html');
        $('#id_events').load('/eframe?chan=PEER_T');
    });