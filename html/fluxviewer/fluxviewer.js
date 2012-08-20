	debug = function (msg) { if (window.console != undefined) { console.log(msg); } }
	
	var showers = [
		{code:"QUA", r:"2.1", begin:"01-01", end:"01-05", max:"01-03", name:"Quadrantids        "},
		{code:"ACE", r:"2.0", begin:"01-28", end:"02-21", max:"02-07", name:"alpha-Centaurids   "},			
		{code:"DLE", r:"3.0", begin:"02-15", end:"03-10", max:"02-24", name:"delta-Leonids      "},
		{code:"GNO", r:"2.4", begin:"02-25", end:"03-22", max:"03-13", name:"gamma-Normids      "},
		{code:"LYR", r:"2.1", begin:"04-16", end:"04-25", max:"04-22", name:"Lyrids             "},
		{code:"PPU", r:"2.0", begin:"04-15", end:"04-28", max:"04-24", name:"pi-Puppids         "},
		{code:"ETA", r:"2.4", begin:"04-19", end:"05-28", max:"05-05", name:"eta-Aquarids       "},
		{code:"ELY", r:"3.0", begin:"05-03", end:"05-12", max:"05-09", name:"eta-Lyrids         "},
		{code:"JBO", r:"2.2", begin:"06-22", end:"07-02", max:"06-27", name:"June-Bootids       "},
		{code:"PAU", r:"3.2", begin:"07-15", end:"08-10", max:"07-28", name:"Piscis-Austrinids  "},
		{code:"SDA", r:"3.2", begin:"07-12", end:"08-19", max:"07-28", name:"S-delta-Aquarids   "},
		{code:"CAP", r:"2.5", begin:"07-03", end:"08-15", max:"07-30", name:"alpha-Capricornids "},			
		{code:"PER", r:"2.2", begin:"07-17", end:"08-24", max:"08-12", name:"Perseids           "},
		{code:"KCG", r:"3.0", begin:"08-03", end:"08-25", max:"08-17", name:"kappa-Cygnids      "},
		{code:"AUR", r:"2.5", begin:"08-25", end:"09-8 ", max:"09-01", name:"alpha-Aurigids     "},
		{code:"SPE", r:"3.0", begin:"09-05", end:"09-17", max:"09-09", name:"September-Perseids "},
		{code:"DAU", r:"3.0", begin:"09-18", end:"10-10", max:"10-04", name:"delta-Aurigids     "},
		{code:"OCA", r:"3.0", begin:"10-05", end:"10-07", max:"10-06", name:"Oct-Camelopardalids"},
		{code:"GIA", r:"2.6", begin:"10-06", end:"10-10", max:"10-08", name:"Draconids          "},
		{code:"TUM", r:"3.0", begin:"10-12", end:"10-18", max:"10-16", name:"tau-Ursa-Majorids  "},
		{code:"EGE", r:"3.0", begin:"10-13", end:"10-27", max:"10-18", name:"epsilon-Geminids   "},
		{code:"ORI", r:"2.5", begin:"10-02", end:"11-07", max:"10-21", name:"Orionids           "},
		{code:"LMI", r:"3.0", begin:"10-19", end:"10-27", max:"10-24", name:"Leo-Minorids       "},
		{code:"STA", r:"2.3", begin:"09-25", end:"11-25", max:"10-10", name:"S-Taurids          "},
		{code:"NTA", r:"2.3", begin:"09-25", end:"11-25", max:"11-12", name:"N-Taurids          "},
		{code:"LEO", r:"2.5", begin:"11-10", end:"11-23", max:"11-17", name:"Leonids            "},
		{code:"AMO", r:"2.4", begin:"11-15", end:"11-25", max:"11-21", name:"alpha-Monocerotids "},
		{code:"PHO", r:"2.8", begin:"11-28", end:"12-09", max:"12-06", name:"December-Phoenicids"},
		{code:"PUP", r:"2.9", begin:"12-01", end:"12-15", max:"12-07", name:"Puppid-Velids      "},
		{code:"MON", r:"3.0", begin:"11-27", end:"12-17", max:"12-09", name:"Monocerotids       "},
		{code:"HYD", r:"3.0", begin:"12-03", end:"12-15", max:"12-12", name:"sigma-Hydrids      "},
		{code:"GEM", r:"2.6", begin:"12-07", end:"12-17", max:"12-14", name:"Geminids           "},
		{code:"COM", r:"3.0", begin:"12-12", end:"12-31", max:"12-19", name:"Coma-Berenicids    "},
		{code:"URS", r:"3.0", begin:"12-17", end:"12-26", max:"12-22", name:"Ursids             "},	
	];	


	
	function get_binarg_meteors() {
		return Math.round(Math.pow(10, $( "#slider-meteors" ).slider( "value" )))
	}

	function get_binarg_eca() {
		return Math.round(Math.pow(10, $( "#slider-eca" ).slider( "value" )))
	}
	
	function get_binarg_eca_pretty() {
		return get_binarg_eca()*1000 +" km<sup>2</sup> &middot; h ";
	}
	
	function duration_to_hours(duration) {
		hours = Math.pow(10, duration);
		// Ensure the value given to the webservice call is exactly equal to the value shown to the user
		if (hours < 1.01) {
			return Math.round(hours*60.0)/60.0;
		} else if (hours < 12) {
			return hours.toFixed(1);
		} else if (hours < 24) {
			return hours.toFixed(0);
		} else {
			return Math.round(hours/24.0)*24.0;
		}		
		return hours;
	}
	
	function format_duration(duration) {
		hours = Math.pow(10, duration);
		if (hours < 1.01) {
			return Math.round(hours*60.0)+" mins";
		} else if (hours < 12) {
			return hours.toFixed(1)+" hours";
		} else if (hours < 24) {
			return hours.toFixed(0)+" hours";
		} else {
			return Math.round(hours/24.0)+" days";
		}
	}

	function loadplot() {
		$('#status').html("<span style='font-size:1.5em; color:#666666;'><img src='lib/images/pleasewait.gif' style='vertical-align:middle;'/> Please wait</span>")
		$('#profile').html("");
		
		//url = "http://vmo.imo.net/flx/fluxviewer/api_v1.php?";
		url = "http://vmo.imo.net/flx/getfluxpage.php?"
		url += "shower=" + $( '#showercode' ).val();
		url += "&begin_iso=" + $('#begin').val();      
		url += "&end_iso=" + $('#end').val();
		
		url += "&min_eca=" + get_binarg_eca();
		url += "&min_meteors=" + get_binarg_meteors();
		
		url += "&min_interval=" + duration_to_hours($("#slider-duration").slider("values", 0));
		url += "&max_interval=" + duration_to_hours($("#slider-duration").slider("values", 1));  
		url += "&popindex=" + $( '#popindex' ).val();
		url += "&gamma=" + $( '#gamma' ).val();
		url += "&stations=" + $( '#stations' ).val();
		url += "&output=" + $( '#output' ).val();
		
		ymax = $('#ymax').val();
		if ( ymax ) {
			url += "&ymax=" + ymax;
		}
		
		$('#profile').load( encodeURI(url), function() {
				$('#status').html("");
				debug("Call: "+url);
		});
	}
	
	$(function() {
		$( "#settings-tabs" ).tabs();		
				
		$( "#slider-meteors" ).slider({
			min: -0.35,
			max: 3.0,
			step:0.0001,
			value: Math.log(20) / Math.log(10),
			slide: function( event, ui ) {
				$( "#binarg-meteors" ).html( get_binarg_meteors() );
			}
		});
		
		$( "#binarg-meteors" ).html( get_binarg_meteors() );

		$( "#slider-eca" ).slider({
			min: -0.35,
			max: 3.0,
			step:0.0001,
			value: Math.log(20) / Math.log(10),
			slide: function( event, ui ) {
				$( "#binarg-eca" ).html( get_binarg_eca_pretty() );
			}
		});
		
		$( "#binarg-eca" ).html( get_binarg_eca_pretty() );
		
		$( "#slider-duration" ).slider({
			range: true,
			min: -1.7,
			max: 3.38,
			step:0.001,
			//values: [ Math.log(0.166667) / Math.log(10), Math.log(24) / Math.log(10) ],
			values: [ Math.log(24) / Math.log(10), Math.log(24) / Math.log(10) ],
			slide: function( event, ui ) {
				$( "#duration" ).text( format_duration(ui.values[0]) + " - " + format_duration(ui.values[1]) );
			}
		});
		$( "#duration" ).text( format_duration( $("#slider-duration").slider("values", 0) ) +
			" - " + format_duration( $("#slider-duration").slider("values", 1) ) );
		
		
		
		
		$( "#selectable" ).selectable({
				filter:'tr,td,th', 
				
		});
		
			
		$( "button.update, button.link").button();
		$( "button.update" ).click(function() {  
			loadplot(); 
		});
		
		
		/*		
		var options = ["PER","GEM","LEO",4,5,6,7,8,9,0,'.'];
		var html = '<div class="showerpicker">';
		for(var i = 0, len = options.length; i < len; i++){
			html += '<a>'+options[i]+'</a> ';
		}
		html += '</div>';
		*/
		
		$( "#showercode" ).change(function() {  
				showerchoice = $("#showercode").val();
				today = new Date();
				
				if (showerchoice == "SPO" || showerchoice == "ANT") {
					$("#begin").val( today.getFullYear()+"-"+(today.getMonth()+1)+"-01 00:00:00" );
					$("#end").val( today.getFullYear()+"-"+(today.getMonth()+2)+"-01 00:00:00" );
					$("#popindex").val( "3.0" );
				} else {
					/* Loop through array of shower data */
					for(var i=0, len = showers.length; i < len; i++) {
						if (showers[i].code == showerchoice) {
							
							$("#begin").val( today.getFullYear() + "-" + showers[i].begin + " 00:00:00" );
							$("#end").val( today.getFullYear() + "-" + showers[i].end + " 00:00:00");
							$("#popindex").val( showers[i].r );
							break;
						}
					}
				}
		});		
		
		
		
		loadplot();
	});
