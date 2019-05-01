'use strict';

const obj = require('./pokedex.js');
const fs = require('fs');

let ab = obj.BattlePokedex;

for(var key in ab){

    delete ab[key]["heightm"];
    delete ab[key]["weightkg"];
    delete ab[key]["color"];
    delete ab[key]["evos"];
    delete ab[key]["evos"];
    delete ab[key]["prevo"];
    delete ab[key]["genderRatio"];

    ab[ab[key]["species"]] = ab[key]

    if(ab[key]["species"] != key){
        delete ab[key]
    }



}

// writes 'https://twitter.com/#!/101Cookbooks', 'http://www.facebook.com/101cookbooks'
fs.writeFileSync('./pokedex.json', JSON.stringify(ab) , 'utf-8');
