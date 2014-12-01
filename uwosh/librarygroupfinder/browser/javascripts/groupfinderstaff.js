
jq(document).ready(function(){
    jq('#gf_staff_listing_chooser').datepicker({dateFormat: 'yy-mm-dd'});
	jq('#gf_staff_listing_chooser').bind('change', function() { getNewList(); });
	
	jq('#gf_staff_date_chooser').datepicker({dateFormat: 'yy-mm-dd'});
	jq('#gf_staff_date_chooser').bind('change', function() { dateWasPicked(); });
	
	jq('#gf_staff_start_chooser').bind('change', function() { timePicked(); });
	jq('#gf_staff_end_chooser').bind('change', function() { loadLocations(); });
	
	jq('#gf_staff_public_chooser').bind('change', function() { isPublicEvent(); });
	isPublicEvent(); 
	
	//Simple Verification that Fields are filled.
	checkFields();
});


function isValidEmail() {
	var email = jq.trim(jq('#gf_staff_email').val());
	var filter = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
	if (email.indexOf("@uwosh.edu") == -1)
		email = email + "@uwosh.edu";
	if ((email.length < 12 || email.length > 18) )
		return false;
	if (filter.test(email)) 
		return true;
	else 
		return false;
}

function checkFields(){
	jq('#gf_staff_submit').click(function(){
		if(!isValidEmail())
			return alertBox("Invalid Email or Missing Email");
		else if(jq.trim(jq('#gf_staff_desc_chooser').val()).length < 4 )
			return alertBox("Missing Description");
		else if(jq.trim(jq('#gf_staff_date_chooser').val()).length < 4 )
			return alertBox("Missing Date");
		else if(jq.trim(jq('#gf_staff_start_chooser :selected').val()) == "" )
			return alertBox("Missing Start Time");
		else if(jq.trim(jq('#gf_staff_end_chooser :selected').val()) == 0 )
			return alertBox("Missing Duration");
		else if(jq.trim(jq('#gf_staff_location_chooser :selected').val()).length < 4 )
			return alertBox("Missing Location");	
	});
}
function alertBox(msg) {
	alert("All Fields Required. " + msg);
	return false;
}


function isPublicEvent(){
	
	if(!jq('#gf_staff_public_chooser').is(':checked')) {
		jq('#gf_staff_desc_chooser').val("Private Event");
		jq('#gf_staff_desc_chooser').attr('readonly','readonly');
		jq('#gf_staff_desc_chooser').css({'color':'gray','font-style':'italic'});
	}
	else {
		jq('#gf_staff_desc_chooser').val("");
		jq('#gf_staff_desc_chooser').removeAttr('readonly');
		jq('#gf_staff_desc_chooser').css({'color':'black','font-style':'normal'});
	}
	
}


function dateWasPicked() {
	resetFields();
	var url = getPartialURL() + "/getHours";
	var parameters = "?date="+jq('#gf_staff_date_chooser').val()+"&option=all";

	jq('#gf_staff_start_chooser').html('');
	jq('.gf_loading1').show();
	jq.getJSON(url+parameters, function(data){

		if(data.closed == "1"){
			jq('#gf_staff_start_chooser').html('<option value="empty">Library is closed</option>');
			jq('#gf_staff_start_chooser').attr('disabled','disabled');
		} 
		else {
			jq('#gf_staff_start_chooser').removeAttr('disabled');
			jq('#gf_staff_start_chooser').append('<option value=""> </option>');
			
			// Start of Hours
			jq('#gf_staff_start_chooser').append('<option value="' + timeTransformBare(data.opens, data.opens_min) + '">' + timeTransformPM(data.opens, data.opens_min) + '</option>');
			if (data.opens_min == 0) 
				jq('#gf_staff_start_chooser').append('<option value="' + timeTransformBare(data.opens, 30) + '">' + timeTransformPM(data.opens, 30) + '</option>');
			// Start of Hours Stop
			
			// Middle of Hours
			m_start = data.opens + 1;
			m_end = data.closes - 1;
			for (var i = m_start; i <= m_end && i < 22; i++){
				jq('#gf_staff_start_chooser').append('<option value="' + timeTransformBare(i, 0) + '">' + timeTransformPM(i, 0) + '</option>');
				jq('#gf_staff_start_chooser').append('<option value="' + timeTransformBare(i, 30) + '">' + timeTransformPM(i, 30) + '</option>');
			}	
			// Middle of Hours Stop

			//End of Hours
			if (data.closes < 22)
				if (data.closes_min == 0) 
					jq('#gf_staff_start_chooser').append('<option value="' + timeTransformBare(data.closes, data.closes_min) + '">' + timeTransformPM(data.closes, data.closes_min) + '</option>');
				else {
					jq('#gf_staff_start_chooser').append('<option value="' + timeTransformBare(data.closes, 0) + '">' + timeTransformPM(data.closes, 0) + '</option>');
					jq('#gf_staff_start_chooser').append('<option value="' + timeTransformBare(data.closes, 30) + '">' + timeTransformPM(data.closes, 30) + '</option>');
				}
			//End of Hours Stop
		}
		jq('.gf_loading1').hide();
	});
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


function timePicked()
{
	jq('#gf_staff_end_chooser').removeAttr('disabled');
	jq('#gf_staff_end_chooser').html('');
	jq('#gf_staff_end_chooser').append('<option value="0"></option>');
	jq('#gf_staff_end_chooser').append('<option value="30">30 Minutes</option>');
	jq('#gf_staff_end_chooser').append('<option value="60">1 Hour</option>');
	jq('#gf_staff_end_chooser').append('<option value="90">1 1/2 Hours</option>');
	jq('#gf_staff_end_chooser').append('<option value="120">2 Hours</option>');
}


function loadLocations()
{
	var time = jq('#gf_staff_start_chooser').val();
	var date = jq('#gf_staff_date_chooser').val();
	var duration = jq('#gf_staff_end_chooser').val();
	jq('#gf_staff_location_chooser').removeAttr('disabled');
	
	
	url = getPartialURL() + "/getLocations";
	parameters = "?time="+time+"&date="+date+"&duration="+duration;
	
	jq('#gf_staff_location_chooser').html('');
	jq('.gf_loading2').show();
	jq.getJSON(url+parameters, function(data){
		
		for(var i = 0; i < data.response.length; i++)
			jq('#gf_staff_location_chooser').append('<option value="'+data.response[i].UID+'">'+
													data.response[i].Name+ " - " +data.response[i].DirectionsShort+
													'</option>');
		jq('.gf_loading2').hide();
    });
}



function resetFields() {
	jq('#gf_staff_start_chooser').attr('disabled','disabled');
	jq('#gf_staff_start_chooser').html('<option value="">Select a date above.</option>');
	
	jq('#gf_staff_end_chooser').attr('disabled','disabled');
	jq('#gf_staff_end_chooser').html('<option value="">Select a start time above.</option>');
	
	jq('#gf_staff_location_chooser').attr('disabled','disabled');
	jq('#gf_staff_location_chooser').html('<option value="">Select a duration above.</option>');
}

function getNewList(){
	jq('.gf_loading3').show();
	url = getPartialURL() + "/staff/subview_gfstaff";
	parameters="?form.date="+jq('#gf_staff_listing_chooser').val();
	jq('#gf_staff_listing').load(url+parameters, function(){
		jq('.gf_loading3').hide();
	});
}

function getPartialURL() {
    var url = window.location.href;
    var end = url.indexOf("/groupfinder") + 12;
    url = url.substring(0,end)
    return url;
}