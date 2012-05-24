jQuery(document).ready(function(){
        $('#id_graph').html('<strong>Universe Topology</strong><hr/><img src="/ugraph.png">');
        $('#id_events').load('/eframe?chan=peer');
    });