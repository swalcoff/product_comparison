$(document).ready(function(){
  $("#output1").hide()
  $("#output2").hide()
})
var api_url = 'https://bfjrougxi0.execute-api.us-west-1.amazonaws.com/test/getsentiment'
var val1, val2;
$('#submitButton').on('click', function(){
  document.getElementById("winner").innerHTML = "Loading...";
  $('#winner').show()
  $.when(
    console.log("request sent..."),
    $.ajax({
      url: api_url,
      cache: false,
      type: 'GET',
      data: {"query": $('#msg1').val()},
      success: function(data){
        var sentiment = JSON.parse(data.body).sentiment
                val1 = sentiment
        console.log(sentiment)
        document.getElementById("output1").innerHTML = sentiment
      }
    }),
    $.ajax({
      url: api_url,
      cache: false,
      type: 'GET',
      data: {"query": $('#msg2').val()},
      success: function(data){
        var sentiment = JSON.parse(data.body).sentiment
                val2 = sentiment
        console.log(sentiment)
        document.getElementById("output2").innerHTML = sentiment		        	}
    }),
  ).then(function(){
        var winner;
        if(val1 > val2)
        {
            winner = $('#msg1').val();
        } else
        {
            winner = $('#msg2').val();
        }

        document.getElementById("winner").innerHTML = winner;
        $('#winner').show()
        $("#output1").show();
        $("#output2").show();
  })
})