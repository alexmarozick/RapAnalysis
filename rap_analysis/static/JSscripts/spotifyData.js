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
        function(data){
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
    $('#analyzeP').bind('click', function(){
        console.log("In playlist")
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
            // console.log(data)
            $('#playlistWidget').attr("src",data.result);
        });
    })

}
