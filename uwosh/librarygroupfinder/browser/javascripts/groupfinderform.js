//Storage Container for XML locations in the mainview.
var locationsVIEW;
var example = "'Example: Biology 101'";
var check_desc = false, 
    check_date = false, 
    check_time = false, 
    check_duration = false;

function checker()
{
    jq('#gf_description_chooser').keypress(function(){
        if(jq.trim(jq('#gf_description_chooser').val()).length == 0 ||
           jq.trim(jq('#gf_description_chooser').val()) == example)
        {
            //jq('#gf_description_box').addClass('gf_warning');
            check_desc =  false;
        }
        else
        {
            //jq('#gf_description_box').removeClass('gf_warning');
            check_desc =  true;
        }
    });
    jq('#gf_date_chooser').change(function(){
        var re = /20[0-9][0-9]-[0-1][0-9]-[0-3][0-9]/g;
        if(jq.trim(jq('#gf_date_chooser').val()).match(re) == null)
        {
            jq('#gf_date_box').addClass('gf_warning');
            check_date =  false;
        }
        else
        {
            jq('#gf_date_box').removeClass('gf_warning');
            check_date =  true;
        }
        if(jq.trim(jq('#gf_description_chooser').val()) == example)
        {
            jq('#gf_description_box').addClass('gf_warning');
            check_desc =  false;
        }
        else
        {
            jq('#gf_description_box').removeClass('gf_warning');
            check_desc =  true;
        }
    });
    jq('#gf_time_chooser').change(function(){
        if(jq('#gf_time_chooser').val() == 'empty')
        {
            jq('#gf_time_box').addClass('gf_warning');
            check_time =  false;
        }
        else
        {
            jq('#gf_time_box').removeClass('gf_warning');
            check_time =  true;
        }
    });
    jq('#gf_duration_chooser').change(function(){
        if(jq('#gf_duration_chooser').val() == 'empty')
        {
            jq('#gf_time_box').addClass('gf_warning');
            check_duration = false;
        }
        else
        {
            jq('#gf_time_box').removeClass('gf_warning');
            check_duration = true;
        }
    });
}

function descriptionSelected()
{
    contentCheck();
}

function dateSelected()
{
	var date = jq('#gf_date_chooser').val();
	var url = getPartialURL() + "/getHours";
	var parameters = "?date="+date;
    jq('#gf_location_radios').html('<span>Please select a Time and Date.</span>');
    jq('#gf_time_chooser').attr('disabled','disabled');
    jq('#gf_duration_chooser').attr('disabled','disabled');
    jq('.gf_loading1').show();
	jq.getJSON(url+parameters, function(data){
		if(data.closed == "1")
        {
            jq('#gf_time_chooser').html('<option value="empty">Library is closed</option>');
            jq('#gf_time_chooser').attr('disabled','disabled');
            jq('#gf_duration_chooser').attr('disabled','disabled');
        }
		else if (data.past == "1")
		{
            jq('#gf_time_chooser').html('<option value="empty">No more times available</option>');
            jq('#gf_time_chooser').attr('disabled','disabled');
            jq('#gf_duration_chooser').attr('disabled','disabled');
		}
		else if (data.past == "0")
		{
			jq('#gf_time_chooser').html('<option value="empty"></option>');
            jq('#gf_time_chooser').removeAttr('disabled');
            jq('#gf_duration_chooser').removeAttr('disabled');


			// Start of Hours
			if (data.opens < data.closes) {
				jq('#gf_time_chooser').append('<option value="' + timeTransformBare(data.opens, data.opens_min) + '">' + timeTransformPM(data.opens, data.opens_min) + '</option>');
				if (data.opens_min == 0) 
					jq('#gf_time_chooser').append('<option value="' + timeTransformBare(data.opens, 30) + '">' + timeTransformPM(data.opens, 30) + '</option>');
			}
			// Start of Hours Stop
			
			// Middle of Hours
			m_start = data.opens + 1;
			m_end = data.closes - 1;
			for (var i = m_start; i <= m_end; i++){
				jq('#gf_time_chooser').append('<option value="' + timeTransformBare(i, 0) + '">' + timeTransformPM(i, 0) + '</option>');
				jq('#gf_time_chooser').append('<option value="' + timeTransformBare(i, 30) + '">' + timeTransformPM(i, 30) + '</option>');
			}	
			// Middle of Hours Stop

			//End of Hours
			if (data.closes < 22)
				if (data.closes_min == 0) 
					jq('#gf_time_chooser').append('<option value="' + timeTransformBare(data.closes, data.closes_min) + '">' + timeTransformPM(data.closes, data.closes_min) + '</option>');
				else {
					jq('#gf_time_chooser').append('<option value="' + timeTransformBare(data.closes, 0) + '">' + timeTransformPM(data.closes, 0) + '</option>');
					jq('#gf_time_chooser').append('<option value="' + timeTransformBare(data.closes, 30) + '">' + timeTransformPM(data.closes, 30) + '</option>');
				}
			//End of Hours Stop
			
			
		}
		else
		{
            jq('#gf_time_chooser').html('<option value="empty">Select a Date</option>');
            jq('#gf_time_chooser').attr('disabled','disabled');
            jq('#gf_duration_chooser').attr('disabled','disabled');
		}
		
        jq('.gf_loading1').hide();
         
        var today = new Date();
        var checkDate = new Date(date.replace(/-/g, "/"));
         
        if((today.getDate() == checkDate.getDate()) && (today.getMonth() == checkDate.getMonth()))
            jq('.gf_date_warning').fadeIn('fast');
        else
            jq('.gf_date_warning').fadeOut('fast');
	});
    contentCheck();
}




function timeTransformBare(hours,minutes) {
	var fm = "00";
	if (minutes < 30)
		fm = "00";
	else 
		fm = "30";
	return hours + ":" + fm;
}

function timeTransform(hours,minutes) {
	var fh = -1;
	var fm = "00";
	if (hours > 12)
		fh = hours-12;
	else
		fh = hours;
	if (minutes < 30)
		fm = "00";
	else 
		fm = "30";
	return fh + ":" + fm;
}

function timeTransformPM(hours,minutes) {
	var half = "AM";
	if (hours < 12)
		half = "AM";
	else if (hours >= 12)
		half = "PM";
	return timeTransform(hours,minutes) + " " + half;
}


function timeSelected()
{
	var time = jq('#gf_time_chooser').val();
	var duration = jq('#gf_duration_chooser').val();
	var date = jq('#gf_date_chooser').val();

	if(duration != "empty" && time != "empty")
	{
        contentCheck();
		loadLocations(date,time,duration);
		jq('#gf_location_chooser').fadeIn('fast');
	}
}


function loadLocations(date,time,duration)
{
	url = getPartialURL() + "/getLocations";
	parameters = "?time="+time+"&date="+date+"&duration="+duration;
	jq('#gf_location_radios').html('');
	jq.getJSON(url+parameters, function(data){
		locationsFORM = jq.extend({},data.response);
		for(var i = 0; i < data.response.length; i++)
			jq('#gf_location_radios').append('<input onclick="displayLocationContent('+i+')" type="radio" value="'+data.response[i].UID+'" name="form.location" />'+
											 '<span class="gf_cursor1" onclick="displayLocationContent('+i+')">'+data.response[i].Name+' - '+data.response[i].DirectionsShort+'</span><br />');
        displayLocationContent(0); //Display First Item
        //jq('input[name="form.location"]:first').attr('checked','checked');
    });
	
	if( jq("#gf_location_content_panel").css("display") == "none" )
        jq('.gf_help_panel').fadeOut('fast',function() {
           jq('#gf_location_content_panel').fadeIn('slow');
        });
    //alert(check_desc + " " + check_date + " " + check_time + " " + check_duration);
}

function displayLocationContent(value)
{
	jq('.gf_location_top').hide(); //Hide for reload
    contentCheck();
    jq('input[name="form.location"]:eq('+value+')').attr('checked','checked');
	jq('#gf_panel_location').html(locationsFORM[value].Name);
	jq('#gf_panel_directions').html(locationsFORM[value].Directions);
	jq('#gf_panel_roomcontents').html(locationsFORM[value].RoomContents);
	jq('#gf_panel_capacity').html(locationsFORM[value].Capacity);
	jq('#gf_panel_key').html(locationsFORM[value].Key);
	jq('.gf_location_top').html('<img src="'+locationsFORM[value].ImageURL+'" alt="Loading Image..." />').fadeIn('slow');
	jq('#gf_panel_note').html(locationsFORM[value].Note);
}


function contentCheck()
{
    if(check_desc && check_date && check_time && check_duration)
    {
        jq('#gf_submitter').removeAttr('disabled');
        jq('#gf_submitter').css({'filter':'alpha(opacity=100)','-moz-opacity':'1.0','-khtml-opacity':'1.0','opacity':'1.0','cursor':'pointer'});
    }
}

function clearExample()
{
    if(jq('#gf_description_chooser').val() == example)
    {
        jq('#gf_description_chooser').val("");
        jq('#gf_description_chooser').css({'color':'black','font-style':'normal'});
    }
}

function getPartialURL()
{
    var url = window.location.href;
    var end = url.indexOf("/groupfinder") + 12;
    url = url.substring(0,end)
    return url;
}

jq(document).ready(function(){
    jq('#gf_date_chooser').datepicker({dateFormat: 'yy-mm-dd'});
    jq('#gf_description_chooser').val(example);
    jq('#gf_description_chooser').bind('click', function() { clearExample(); });
    jq('#gf_description_chooser').bind('keypress', function() { descriptionSelected(); });
    jq('#gf_date_chooser').bind('change', function() { dateSelected(); });
    jq('#gf_time_chooser').bind('change', function() { timeSelected(); });
    jq('#gf_duration_chooser').bind('change', function() { timeSelected(); });
    checker();
});