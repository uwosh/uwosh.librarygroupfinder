//Storage Container for XML locations in the mainview.
var locationsVIEW;

function loadAllLocations()
{
	url = getPartialURL() + "/getLocations";
	parameters = "?option=all";
	jq.getJSON(url+parameters, function(data){
		locationsVIEW = jq.extend({},data);
    });
}

function displayLocation(id)
{
    found = false;
    for(var i = 0; i < locationsVIEW.response.length && !found; i++)
        if(locationsVIEW.response[i].UID == id)
        {
            jq('#gf_panel_location').html(locationsVIEW.response[i].Name);
            jq('#gf_panel_directions').html(locationsVIEW.response[i].Directions);
            jq('#gf_panel_roomcontents').html(locationsVIEW.response[i].RoomContents);
            jq('#gf_panel_capacity').html(locationsVIEW.response[i].Capacity);
            jq('#gf_panel_key').html(locationsVIEW.response[i].Key);
            jq('.gf_location_top').html('<img src="'+locationsVIEW.response[i].ImageURL+'" alt="Loading Image..." />');
            jq('.gf_background_fader').fadeIn('fast');
            jq('.gf_floating_display').fadeIn('fast');
        }
}

function closeLocation()
{
    jq('.gf_background_fader').fadeOut('fast');
    jq('.gf_floating_display').fadeOut('fast');
}

function setAttendee(id)
{
    url = getPartialURL() + "/attendee";
	parameters = "?option=set&id="+id;
	jq.getJSON(url+parameters, function(data){
        if(data.response.success == "1")
        {
            if(data.response.count == 1)
                jq('#'+id+" .gf_attendence").html(data.response.count + " Student Attending");
            else 
                jq('#'+id+" .gf_attendence").html(data.response.count + " Students Attending");
            jq('#'+id+" .gf_attendence_clicks .gf_links2").unbind('click');
            jq('#'+id+" .gf_attendence_clicks .gf_links2").html('Remove Attendence?');
            
            jq('#'+id+" .gf_attendence_clicks .gf_links2").bind('click', function() {
                removeAttendee(id);
            });
        }
        else if(data.response.success == "2") 
        {
            window.location = window.location.href; //If not logged in, response "2" force refresh.
        }
    });
}

function removeAttendee(id)
{
    url = getPartialURL() + "/attendee";
	parameters = "?option=remove&id="+id;
	jq.getJSON(url+parameters, function(data){
        if(data.response.success == "1")
        {
            if(data.response.count == 1)
                jq('#'+id+" .gf_attendence").html(data.response.count + " Student Attending");
            else
                jq('#'+id+" .gf_attendence").html(data.response.count + " Students Attending");
            jq('#'+id+" .gf_attendence_clicks .gf_links2").unbind('click');
            jq('#'+id+" .gf_attendence_clicks .gf_links2").html('Join?');
            
            jq('#'+id+" .gf_attendence_clicks .gf_links2").bind('click', function() {
                setAttendee(id);
            });
        }
        else if(data.response.success == "2") 
        {
            window.location.replace(window.location.href); //If not logged in, response "2" force refresh.
        }
    });
}


function search()
{
    var term = jq.trim(jq('#gf_search_box').val()).toLowerCase();
    var elms = jq('.gf_view_border');  
    elms.each( function () {  
        if(jq(this).find ('.gf_title').html().toLowerCase().indexOf(term) > -1)
            jq(this).css('display','block');
        else
            jq(this).css('display','none');
    });
    if(term == "")
        jq('.gf_view_border').css('display','block');
}

function getPartialURL()
{
    var url = window.location.href;
    var end = url.indexOf("/groupfinder") + 12;
    url = url.substring(0,end);
    return url;
}


function clearSearchBox()
{
	jq('#gf_search_box').attr("value","");
}

jq(document).ready(function(){
    jq('.gf_floating_display').click(function() {
        closeLocation();
    });
    jq('#gf_search_box').keyup(function() {
        search();
    });

    jq('.gf_view_border .gf_links2').click(function() {
    
        if(jq(this).attr('data-fun') == "set")
            setAttendee(jq(this).attr('data-gfid'));
        if(jq(this).attr('data-fun') == "remove")
            removeAttendee(jq(this).attr('data-gfid'));
    });
    
    
    jq('.gf_locations').click(function() {
         displayLocation(jq(this).attr('data-location'));
    });
    
	
	jq('#gf_search_x').click(function() {
		clearSearchBox();
		search();
	});
    loadAllLocations();
});