


  // /season/delete-player/<player>/<season>




function getOutPlyer(season, player, index){

    // alert(season);
    // alert(player);
    // $('#playerin'+index+'').fadeOut();
    // $.ajax({
    //   url:"/season/delete/"+season_delete_ide+"",
    //   type:"POST",
    //   data:{season_delete_ide: season_delete_ide},
    //   success:function()
    //   {
      //   $('#update-player-list').val('Updated');

        $('#playerout-delete'+index+'').modal('show');
      //   setTimeout(function(){
      //   $('#info-updated').modal("hide");
      
      // }, 2500);
      // }
      // });
}

// function getOutPlyerDelete(season, player, index){

//     // alert(season);
//     // alert(player);
//     // $('#playerin'+index+'').fadeOut();
//     $.ajax({
//        url:"/season/delete-player/"+season+"/"+player+"",
//        type:"POST",
//        data:{season_delete_ide: season_delete_ide},
//        success:function()
//        {
//          $('#update-player-list').val('Updated');

//         $('#playerout-delete'+index+'').modal('show');
//          setTimeout(function(){
//          $('#info-updated').modal("hide");
      
//        }, 2500);
//        }
//      });
// }




function getOutPlyerDelete(season, player, index){
  $.ajax({
     url: "/season/delete-player/" + player + "/" + season,
     type: "POST",
     data: {season_delete_ide: season},  // Uistite sa, že táto dáta sú správne očakávané na serveri
     success: function(response) {
       if(response.status === 'success') {
           // Ak je odpoveď úspešná, skryte príslušný element
           $('#playerout-delete'+index+'').modal('hide');
           setTimeout(function(){
             $('#playerin'+index).fadeOut();
           }, 400);

          // alert(response.message);  // Alebo aktualizujte užívateľské rozhranie iným spôsobom
       } else {
           // Spracovanie chyby
          // alert(response.message);
       }
     }
  });
}










//get your element and prevent mousedown from firing  
document.body.addEventListener('dblclick',function(e){ 
	e.preventDefault(); 
}); 

async function deleteNote(noteId) {
  await fetch('/delete-note', {
    method: 'POST',
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    // window.location.href = "/";
    removeFadeOut(document.getElementById('row' + noteId), 500)
  })
}

// upadate DUEL

async function updateDuel(looopindex) {
  inputs = document.getElementById('checked[' + looopindex + ']')
  player = document.getElementById('player[' + looopindex + ']')
  duel = document.getElementById('duel[' + looopindex + ']')
  await fetch('/update-duel', {
    method: 'POST',
    body: JSON.stringify({
      duelCheck: inputs.checked + ',' + duel.value + ',' + player.value,
    }),
  }).then((_res) => {
    div1 = document.getElementById('confirmed[' + looopindex + ']')
    if (
      document.getElementById('checked[' + looopindex + ']').checked == true
    ) {
      div1.innerHTML = ''
    } else {
      var div1 = document.getElementById('confirmed[' + looopindex + ']')
      div1.innerHTML = '<h4>confirm</h4>'
    }

    inputs = null
    player = null
    duel = null

    // window.location.href = "/";
    //removeFadeOut(document.getElementById("row" + noteId), 500);
  })
}






async function updateRound() {
  inputs = document.getElementById('checked')
  season_id = document.getElementById('season_id')
  round_id = document.getElementById('round_id')
  await fetch('/season/'+season_id.value+'/update-round/'+round_id.value+'', {
    method: 'POST',
    body: JSON.stringify({
      duelCheck: inputs.checked + ',' + season_id.value + ',' + round_id.value,
    }),
  }).then((_res) => {
    div1 = document.getElementById('confirmed')
    if (
      document.getElementById('checked').checked == true
    ) {
      div1.innerHTML = '<h4>Opened Round</h4>'
    } else {
      var div1 = document.getElementById('confirmed')
      div1.innerHTML = '<h4>Closed Round</h4>'
    }

    inputs = null
    player = null
    duel = null

    // window.location.href = "/";
    //removeFadeOut(document.getElementById("row" + noteId), 500);

  })
}


async function viewGroup(season, group, round) {
  // var location_href = document.getElementById('view_group_'+group+'')
  // location_href.innerHTML =
  //   '<i class="fa fa-circle-o-notch fa-spin" style="margin-left:15px;padding:9px;"></i>'

  await fetch('/login', {
    method: 'POST',
    // body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    setTimeout(function(){
      // location_href.innerHTML = 'Free Demo'
      window.location.href = "/season/"+season+"/group/"+group+"/round/"+round+"";
    },500)
  })
}

function spinner() {
  var email = document.getElementById('email').value;
  var password = document.getElementById('password').value;
// alert(email);

  if(email!='' && password!=''){
  document.getElementsByClassName("loader")[0].style.display = "block";
  }
}

async function locationHref(url) {
  var location_href = document.getElementById('location_href_'+url+'')
  var user = document.getElementById('user')
  // alert(user.value);
  location_href.innerHTML =
  '<i class="fa fa-circle-o-notch fa-spin" ></i>'
  
  await fetch('/login', {
    method: 'POST',
    // body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    setTimeout(function(){
      // location_href.innerHTML = 'Free Demo'
      // if(user){
        window.location.href = "/"+url+"";
        // location_href.innerHTML = '<i class="fa fa-circle-o-notch fa-spin" style="transition-duration: 3s;opacity:0;margin-left:15px;padding:9px;"></i>'
      // }else{
      //   window.location.href = "/"+url+"";
      //   location_href.innerHTML = '<i class="fa fa-circle-o-notch fa-spin" style="transition-duration: 3s;opacity:0;margin-left:15px;padding:9px;"></i>'
      // }
    },500)
  })
}

async function updateDuel2(looopindex) {
  const body = document.body
  var result = document.getElementById('user_duel_result[' + looopindex + ']')
  var player = document.getElementById('user_duel_id[' + looopindex + ']')
  var duel = document.getElementById('duel_id[' + looopindex + ']')
  if (looopindex == 1) {
    var result_oponent = document.getElementById('user_duel_result[2]')
    var player_oponent = document.getElementById('user_duel_id[2]')
    var duel_oponent = document.getElementById('duel_id[2]')
  } else {
    var result_oponent = document.getElementById('user_duel_result[1]')
    var player_oponent = document.getElementById('user_duel_id[1]')
    var duel_oponent = document.getElementById('duel_id[1]')
  }
  // alert(result.value)

  var spin = document.getElementById('updateDuelButton[' + looopindex + ']')

  if (
    result.value >= 0 &&
    result.value <= 6 &&
    (result.value != result_oponent.value || result.value == 0)
  ) {
    spin.innerHTML =
      '<i class="fa fa-circle-o-notch fa-spin"></i>'
    time = 500
  } else {
    spin.innerHTML = 'OUT OF RANGE'
    setInterval(function () {
      spin.innerHTML = 'SUBMIT'
    }, 2600)
    return false
  }

  if (
    result_oponent.value >= 0 &&
    result_oponent.value <= 6 &&
    (result.value != result_oponent.value || result.value == 0)
  ) {
    spin.innerHTML =
      '<i class="fa fa-circle-o-notch fa-spin" ></i>'
    var time = 500
  } else {
    spin.innerHTML = 'OUT OF RANGE'
    setInterval(function () {
      spin.innerHTML = 'SUBMIT'
    }, 2600)
    return false
  }

  // alert(result_oponent.value)
  // alert(player_oponent.value)
  // alert(duel_oponent.value)

  // spin = document.getElementById('spin-result-update[' + looopindex + ']')

  await fetch('/update-duel2', {
    method: 'POST',
    body: JSON.stringify({
      duelResult:
        result.value +
        ',' +
        duel.value +
        ',' +
        player.value +
        ',' +
        result_oponent.value +
        ',' +
        duel_oponent.value +
        ',' +
        player_oponent.value,
    }),
  }).then((_res) => {
    //alert(result.value + '~' + duel.value + '~' + result_oponent.value);
    player_name_result = document.getElementById(
      'player-name-result[' + looopindex + ']',
    )

    ele = document.getElementById('user_duel_result[' + looopindex + ']')
    ele.style.visibility = ele.style.visibility == 'visible' ? '' : 'hidden'

    setInterval(function () {
      ele.style.visibility = ele.style.visibility == 'hidden' ? '' : 'visible'
    }, 200)

    setInterval(function () {
      spin.innerHTML = 'SUBMIT'
    }, 500)

    // alert(duelCheck)
    // window.location.href = "/";
    //removeFadeOut(document.getElementById("row" + noteId), 500);
  })
}
// var checkedValue = document.querySelector('.messageCheckbox:checked').value;

// #### chooseGroup

async function chooseGroup(looopindex) {
  var grno = document.getElementById('grno[' + looopindex + ']')
  var grname = document.getElementById('grname[' + looopindex + ']')
  var seasons = document.getElementById('seasons[' + looopindex + ']')

  await fetch('/season/' + seasons.value + '/group/' + grno.value + '', {
    method: 'POST',
    body: JSON.stringify({
      groupList: grno.value + ',' + grname.value + ',' + seasons.value,
    }),
  }).then((_res) => {
    console.log(_res)
    // $("#duels-list").load('/season/'+seasons.value+'/group/'+groupId+'');
    // window.location.href = "/";
    // removeFadeOut(document.getElementById('row' + duelId), 500)
  })
}

async function deleteDuel(duelId) {
  await fetch('/delete-duel', {
    method: 'POST',
    body: JSON.stringify({ duelId: duelId }),
  }).then((_res) => {
    // window.location.href = "/";
    removeFadeOut(document.getElementById('row' + duelId), 500)
  })
}

function removeFadeOut(el, speed) {
  var seconds = speed / 1000
  el.style.transition = 'opacity ' + seconds + 's ease'

  el.style.opacity = 0
  setTimeout(function () {
    el.parentNode.removeChild(el)
  }, speed)
}

// var xhr = new XMLHttpRequest();
// xhr.open("GET", "pythoncode.py?text=" + text, true);
// xhr.responseType = "JSON";
// xhr.onload = function(e) {
//   var arrOfStrings = JSON.parse(xhr.response);
// }
// xhr.send();

document.getElementsByClassName('resultscore').onclick = function () {
  this.select()
}

function GoBackWithRefresh(event) {
  if ('referrer' in document) {
    window.location = document.referrer
    /* OR */
    //location.replace(document.referrer);
  } else {
    window.history.back()
  }
}

//CAROUSEL
// const myCarouselElement = document.querySelector('#productForm')
// const carousel = new bootstrap.Carousel(myCarouselElement, {
//   interval: 2000,
//   wrap: false
// })




function toggleDiv() {
  var divToToggle = document.getElementById("hiddenDiv");
  var showPlayersList = document.getElementById("showPlayersList");
  if (divToToggle.style.display === "none") {
    showPlayersList.innerHTML = "Hide Players List -"; // Priradenie hodnoty "nooke"
    divToToggle.style.display = "block";
  } else {
    showPlayersList.innerHTML = "Show Players List +"; // Priradenie hodnoty "none"
    divToToggle.style.display = "none";
  }
}
function toggleDivHistoryRounds() {
  var divToToggleRounds = document.getElementById("hiddenDivHistory");
  var showHistoryRounds = document.getElementById("showHistoryRounds");
  if (divToToggleRounds.style.display === "none") {
    showHistoryRounds.innerHTML = "Hide History Rounds -"; // Priradenie hodnoty "nooke"
    divToToggleRounds.style.display = "block";
  } else {
    showHistoryRounds.innerHTML = "Show History Rounds +"; // Priradenie hodnoty "none"
    divToToggleRounds.style.display = "none";
  }
}




function showLoader() {
  var button = document.getElementById('ide_season_button');
  button.innerHTML = '<i>creating new round...</i>';
  // Odošlite formulár tu, ak to robíte asynchrónne, inak formulár pokračuje v odosielaní.
}




let formChanged = false;

window.onload = function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');

        inputs.forEach(input => {
            input.addEventListener('change', () => {
                formChanged = true;
            });
        });
    });

    // window.addEventListener('beforeunload', function (e) {
    //     if (formChanged) {
    //         const confirmationMessage = 'You have unsaved changes. Are you sure you want to leave?';
    //         e.returnValue = confirmationMessage; // For older browsers
    //         return confirmationMessage; // For modern browsers
    //     }
    // });
}
