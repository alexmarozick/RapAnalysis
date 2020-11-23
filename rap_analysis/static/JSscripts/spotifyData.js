$(document).ready(function(){
    playlist();
    recent_plays();
});

function recent_plays(){
    $('#analyze-recent').unbind().click(function(){
        console.log("In recent")
        $.getJSON('/_analyzeSpotify',{
            // everything here to sends data to flask and to access the data in flask you would do
            // request.args.get("<key>") where you replace <key> with the name of the key for example
            // to get this data: playlistID: $('#droplistP').val() 
            // you would do request.args.get("playlistID") in flask
            recent_num: $('#recent').val(), // how many of the recent plays should get analzyed.
            type: 'recent'
        },
        function(data){ // TODO create a dropdown list.
            // result of what flask returns which is contained in data.
            // data will be a json 
            var dropList = document.getElementById("droplist-recent-songs"); // get drop down menu wil return null if it doesn't exist yet.
            // console.log(dropList);
            // console.log(selector)
            // console.log(data.result.length)
            // console.log(data.result)
            
            if(dropList == null){ // if the drop list does not exist then create the drop list
                var selector = $('<select></select>').attr("id","droplist-recent-songs").attr("onchange", "recent_song_change()");
                $("#drop-recent-wrapper").append(selector);
            }
            $("#droplist-recent-songs").empty(); // clear the droplist 

            $.each(data.result, function(i){ // go thorugh all the songs and add the option to the selector.
                $("#droplist-recent-songs").append($("<option>" + data.result[i].song + "</option>").data("highlight", data.result[i]));
            });
            document.getElementById("output-box").innerHTML = data.result[0].highlight; // set the output box to have the very first song's highlighting.
        });
    })

}


function playlist(){
    // console.log($('#droplistP').val());
    $('#playlistWidget').attr("src","https://open.spotify.com/embed/playlist/"+$('#droplistP').val());
    $('#analyze-playlist').unbind().click(function(){ // Note to self, use "off" instead of "unbind"
        // console.log("In playlist")
        $.getJSON('/_analyzeSpotify',{
            // everything here to sends data to flask and to access the data in flask you would do
            // request.args.get("<key>") where you replace <key> with the name of the key for example
            // to get this data: playlistID: $('#droplistP').val() 
            // you would do request.args.get("playlistID") in flask
            playlistID: $('#droplistP').val(),
            type: 'playlist'
        },
        function(data){
            // result of what flask returns which is contained in data.
            // data will be a json 
            var dropList = document.getElementById("droplist-playlist-songs"); // get drop down menu wil return null if it doesn't exist yet.
            // console.log(dropList);
            // console.log(selector)
            // console.log(data.result.length)
            // console.log(data.result)
            
            if(dropList == null){ // if the drop list does not exist then create the drop list
                var selector = $('<select></select>').attr("id","droplist-playlist-songs").attr("onchange", "playlist_song_change()");
                $("#drop-playlist-wrapper").append(selector);
            }
            $("#droplist-playlist-songs").empty(); // clear the droplist 

            $.each(data.result, function(i){ // go thorugh all the songs and add the option to the selector.
                $("#droplist-playlist-songs").append($("<option>" + data.result[i].song + "</option>").data("highlight", data.result[i]));
            });
            document.getElementById("output-box").innerHTML = data.result[0].highlight; // set the output box to have the very first song's highlighting.
        });
        return false;
    })

}

function playlist_song_change(){
    // Function that will change the contents of the output box depending on the songs
    // that was choosen from the dropdown list that contains all the songs from the analyzed playlist.
    // console.log($('#droplist-playlist-songs').find(':selected').data('highlight').highlight);
    document.getElementById("output-box").innerHTML =  $('#droplist-playlist-songs').find(':selected').data('highlight').highlight;
}

function recent_song_change(){
    // Function that will change the contents of the output box depending on the songs
    // that was choosen from the dropdown list that contains all the songs from the analyzed playlist.
    // console.log($('#droplistS').find(':selected').attr('data-highlight'));
    // console.log($('#droplist-recent-songs').find(':selected').data('highlight').highlight)
    document.getElementById("output-box").innerHTML =  $('#droplist-recent-songs').find(':selected').data('highlight').highlight;
}