$(document).ready(function(){
    playlist() // when the document is ready run this function to display the playlist in the widget.
});

function recent_plays(){
    // console.log($('#droplistP').val());
    // $('#recentWidget').attr("src","https://open.spotify.com/embed/recent/"+$('#droplistP').val());
    $('#analyzeR').bind('click', function(){
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
            // console.log(data)
            // $('#playlistWidget').attr("src",data.result);
        });
    })

}


function playlist(){
    // console.log($('#droplistP').val());
    $('#playlistWidget').attr("src","https://open.spotify.com/embed/playlist/"+$('#droplistP').val());
    $('#analyzeP').unbind().click(function(){ // Note to self, use "off" instead of "unbind"
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
            var dropList = document.getElementById("droplistS"); // get drop down menu wil return null if it doesn't exist yet.
            console.log(dropList);
            // console.log(selector)
            // console.log(data.result.length)
            // console.log(data.result)
            
            if(dropList == null){ // if the drop list does not exist then create the drop list
                var selector = $('<select></select>').attr("id","droplistS").attr("onchange", "pSongs()");
                $("#dropPSongs").append(selector);
            }
            $("#droplistS").empty(); // clear the droplist 

            $.each(data.result, function(i){ // go thorugh all the songs and add the option to the selector.
                $("#droplistS").append($("<option>" + data.result[i].song + "</option>").attr("data-highlight", data.result[i].highlight));
            });
            document.getElementById("output-box").innerHTML = data.result[0].highlight; // set the output box to have the very first song's highlighting.
        });
        return false;
    })

}

function pSongs(){
    // Function that will change the contents of the output box depending on the songs
    // that was choosen from the dropdown list that contains all the songs from the analyzed playlist.
    // console.log($('#droplistS').find(':selected').attr('data-highlight'));
    document.getElementById("output-box").innerHTML =  $('#droplistS').find(':selected').attr('data-highlight');
}