var glob_start = 0;
var glob_end = 0;
var info_win_open = false;

jq(document).ready(function(){
	jq('#gf_booking_chooser').datepicker({dateFormat: 'yy-mm-dd'});
	jq('#gf_booking_chooser').bind('change', function() { setupDateAction(); checkOtherDateBooks(); });
	
	//http://www.uwosh.edu/library/ws/getLibraryHours?v=2&date=2012-1-26
	

	setupDateAction(); // init

	jq('body').click(function(event){
		clearInfoWindow();
	});

});

function rand() {
	return Math.random() + ""
}

function stop() {
	return false;
}

function checkOtherDateBooks() {
	try{
		var val = jq("#gf_booking_chooser").val();
		jq("#gf_staff_listing_chooser").val(val);
		jq('#gf_staff_listing_chooser').trigger('change');
	}
	catch(e){}
}

function setupDateAction() {
	var date = jq('#gf_booking_chooser').val();
	reset();
	getLocations(function(){
		getHours(date,function(){
			getGroups(function(){
				
			});
		});
	});
}

function reset() {
	jq('#gf_bookings_info').html('');
}


function getGroups(callback) {
	var url = getGroupFinderBaseUrl() + "/bookings?groups=1&s_ts="+glob_start+"&e_ts="+glob_end + "&no_cache="+rand();
	jq.getJSON(url,function(data){
		info = data.response;
		for (i in info) {
			fillSlot(info[i]);
		}
	
		callback();
	});
}



function getLocations(callback) {
	var url = getGroupFinderBaseUrl() + "/bookings?locations=1&no_cache="+rand();
	jq.getJSON(url,function(data){
		info = data.response;
		for (i in info) {
			jq('#gf_bookings_info').append(createLocationContainer(info[i].Title,info[i].UID,info[i].directions));
		}
		callback();
	});
}


function getHours(date,callback) {
	
	var url = "http://www.uwosh.edu/library/ws/getLibraryHours?v=2&alt=jsonp&callback=?&date=" + date + "&no_cache="+rand();
	
	jq.getJSON(url,function(data){
		
		time = data.times[0];
		glob_start = new Number(time.open_loc);
		glob_end = new Number(time.close_loc);
		start = glob_start * 1000
		end = glob_end * 1000
		increment = (1800*1000)

		jq('#gf_bookings_info').children().each(function(){
			for (var i = start; i <= end; i = i + increment) {
				var dt = new Date(i);
				if(time.is_open == 1)
					jq(this).append(createTimeSlot(formatTime(dt), i));
				else
					jq(this).append(createTimeSlot("Library Closed", i));
			}
		});
		callback();
	});
}



function fillSlot(data) {
	jq('#gf_bookings_info').children().each(function(){
		if (data.location == jq(this).attr('data-uid')) {
			fillSlotRange(jq(this),data.id,data.start*1000,data.end*1000);
		}
	});
}


function fillSlotRange(parent,id,start,end) {
	var found = false;
	var complete = false;
	jq(parent).children().each(function(){
		if(jq(this).attr('data-id') == start) {
			found = true;
			unavailable(jq(this),id);
		}
		if (found) 
			if (jq(this).attr('data-id') == end) {
				addBBorder(jq(this));
				return false; //stop loop
			}
			else {
				unavailable(jq(this), id);
			}
	});
}

function unavailable(element,id) {
	jq(element).css({'background-color':'#CC6666','cursor':'pointer'});
	attachInfoLink(element,id);
	rmBBorder(element);
}
function available(element) {
	jq(element).css({'background-color':'#C8C8C8 '});
}

function rmBBorder(element) {
	jq(element).css({'border-bottom':'1px solid #CC6666'});
}
function addBBorder(element) {
	
	jq(element).css({'border-top':'1px solid black','height':'14px'});
}

function formatTime(dt) {
	var hour = dt.getHours();
	var minutes = dt.getMinutes();
	var ap = "AM";
	if (hour   > 11) { ap = "PM"; }
	if (hour   > 12) { hour = hour - 12; }
	if (hour   == 0) { hour = 12; }
	if (minutes < 10) { minutes = "0" + minutes; }
	return hour + ":" + minutes + " " + ap;
}

function attachInfoLink(element,id) {
	jq(element).click(function(){
		if (!info_win_open) {
			clearInfoWindow();
			var marker = document.createElement('span');
			jq(marker).addClass('gf_pop_marker');
			jq(this).append(marker);
			jq('.gf_pop_marker').load(getGroupFinderBaseUrl() + '/bookings_info?id=' + id + "&no_cache="+rand(), function(data){
				info_win_open = true;
			});
		}
	});
}

function bypassInfoClose() {
	info_win_open = false;
}

function clearInfoWindow() {
	if (info_win_open) {
		
		try {
			jq('.gf_pop_marker').remove();
			info_win_open = false;
		} 
		catch (e) {
		}
	}
}

function createTimeSlot(title,id) {
	var element = document.createElement('div');
	jq(element).addClass('gf_timeslot');
	jq(element).attr('data-id',id);
	jq(element).html(title);
	return element;	
}

function createLocationContainer(title,uid,directions) {
	var element = document.createElement('div');
	jq(element).addClass('library_left');
	jq(element).addClass('gf_col_width');
	jq(element).attr('data-uid',uid);
	
	var child_element = document.createElement('div');
	jq(child_element).addClass('gf_col_head');
	jq(child_element).html(title);
	jq(element).append(child_element);
	
	var child_element2 = document.createElement('div');
	jq(child_element2).addClass('gf_col_head_info');
	jq(child_element2).html(directions);
	jq(element).append(child_element2);
	
	return element;	
}


function getGroupFinderBaseUrl() {
    var url = window.location.href;
    var end = url.indexOf("/groupfinder") + 12;
    url = url.substring(0,end)
    return url;
}
