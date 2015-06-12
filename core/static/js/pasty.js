/**
 * Created by dan on 6/10/15.
 */

function get_pasty()
{
    console.log(' -- get pasty -- ');

    if( config )
    {
        $.ajax({
            url: config.url,
            cache: false,
            success: function(data){
                console.log(data)
                $('#wrapper').html(data)
            }
        });
    }
}

jQuery(function(){
    get_pasty();
    setInterval(get_pasty, 15000);
});
