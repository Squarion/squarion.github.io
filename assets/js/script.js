
let listItemCurrentPlayer = document.getElementById(currentPlayer);

listItemCurrentPlayer.querySelector("a").classList.add("current");

lastLetter = '';




function search() {
  let query = document.getElementById('search-bar').value.toLowerCase();
  let playerList = document.getElementById('player-list');
  selection = players.filter((player) => player.slug.includes(query));

  playerList.innerHTML = '';
  let last_letter = "";
  for (player of selection) {
    let letter = player.last_name[0];
    if (last_letter != letter) {
      let element = document.createElement('li');
      element.innerHTML = '<div class="heading">' + letter + '</div>';
      playerList.appendChild(element);
    }
    let element = document.createElement('li');
    element.id = player.slug;
    element.innerHTML = '<a href="' + player.slug + '" class="player">' + player.last_name + ', ' + player.first_name + '</a>';
    if (currentPlayer == player.slug) {
      element.querySelector('a').classList.add("current");
    }
    playerList.appendChild(element);
    last_letter = letter;
  }
}

let tournamentLevels = {
  "G": "Grand Slams",
  "M": "ATP Masters 1000",
  "A": "ATP 500 & 250",
  "O": "Olympics",
  "F": "Tour Finals",
  "D": "Davis Cup"
}

sortTitles("level");



function categorySort(e) {
  let categorySort = document.getElementById("category-sort");

  for (c of categorySort.children) {
    c.classList.remove('pressed');
    e.classList.add('pressed');
  }

  sortBy = e.getAttribute("sort");

  sortTitles(sortBy);
}

function sortTitles(sortBy) {
  console.log(sortBy);
  if (sortBy == "level") {
    let order = Object.keys(tournamentLevels);
    console.log(order);
    titles = titles.sort(function(a, b) {
      return order.indexOf(a.level) - order.indexOf(b.level);
    });
    console.log('titles', titles);
  } else {
    titles = titles.sort((a, b) => a[sortBy].localeCompare(b[sortBy]));
  }

  let titlesReversed = titles.reverse();

  let container = document.getElementById("titles");
  container.innerHTML = '';

  let prev = titlesReversed[0][sortBy];
  let count = 0;


  for (title of titlesReversed) {

    if (prev != title[sortBy]) {
      let heading = document.createElement('h2');

      heading.innerHTML = `<span>${prev}</span> <span class="count">(${count})</span>`;
      if (sortBy == "level") {

        heading.innerHTML = `<span>${tournamentLevels[prev]}</span> <span class="count">(${count})</span>`;
        console.log(heading);

      }
      count = 0;
      container.prepend(heading);
    }
    let element = document.createElement('div');
    element.classList.add("title", "blob", title.surface, title.level);
    element.setAttribute("onclick", "checkClick(this)");
    element.innerHTML = `
    <span class="abbr">${title.abbr}</span>
    <div class="content">
      <span class="info"><span class="year">${title.date}</span><span class="name">${title.name}</span></span>
      <span class="result"><span class="score">${title.score}</span> <span class="vs">vs.</span> <a href="${title.runner_up_slug}" class="opponent">${title.runner_up}&nbsp;&#x203A;</a></span>
    </div>`;
    container.prepend(element);
    prev = title[sortBy];
    count++;
  }

  let heading = document.createElement('h2');
  heading.innerHTML = `<span>${prev}</span> <span class="count">(${count})</span>`;
  if (sortBy == "level") {

    heading.innerHTML = `<span>${tournamentLevels[prev]}</span> <span class="count">(${count})</span>`;
    console.log(heading);
    
  }
  container.prepend(heading);
}


let openedTitle = null;

function checkClick(elem) {

  if (openedTitle == elem) {

    elem.classList.remove("open");
    openedTitle = null;
  } else {
    if (openedTitle != null) {
      openedTitle.classList.remove("open");
      openedTitle = null;
    }

    openedTitle = elem;
    elem.classList.add("open");

  }
}




search();
