function hide(name){$('#id_'+name).toggle()}
function clear(name){$('#id_'+name).html('')}
function refresh(name){
    var url = window.location+'/'+name+'?postprocess=reverse_console&force_template=raw';
    $('#id_'+name).html('loading <a href="'+url+'">"'+url+'"</a>');
    $('#id_'+name).load(url);
}
function refresh_sizes(){
    $('#id_stdout_size').html('..');
    $('#id_stderr_size').html('..');
    function geturl(name){
        var url = window.location.pathname + '/_'+name+'/qsize()?&force_template=raw';
        return url.replace('//','/');
    }
    $('#id_stdout_size').load(geturl('stdout'));
    $('#id_stderr_size').load(geturl('stderr'));
    setTimeout("refresh_sizes()", 3000);
}
$(document).ready(refresh_sizes)
