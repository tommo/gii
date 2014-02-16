return (function()
local nodelist={
["normal.encounter"]={name="normal.encounter",localName="encounter",id="_FSM_normal_encounter",type="state"};
["fight.gun_attack_stop"]={name="fight.gun_attack_stop",localName="gun_attack_stop",id="_FSM_fight_gun_attack_stop",type="state"};
["normal.pre_encounter"]={name="normal.pre_encounter",localName="pre_encounter",id="_FSM_normal_pre_encounter",type="state"};
["fight.attacking.attack_start"]={name="fight.attacking.attack_start",localName="attack_start",id="_FSM_fight_attacking_attack_start",type="state"};
["win.start"]={name="win.start",localName="start",id="_FSM_win_start",type="state"};
["fight.charge"]={name="fight.charge",localName="charge",id="_FSM_fight_charge",type="state"};
["fight.attacking.attack_approach"]={name="fight.attacking.attack_approach",localName="attack_approach",id="_FSM_fight_attacking_attack_approach",type="state"};
["fight.gun_start"]={name="fight.gun_start",localName="gun_start",id="_FSM_fight_gun_start",type="state"};
["win.prize"]={name="win.prize",localName="prize",id="_FSM_win_prize",type="state"};
["fight.long_charge_release"]={name="fight.long_charge_release",localName="long_charge_release",id="_FSM_fight_long_charge_release",type="state"};
["fight.counter_wait"]={name="fight.counter_wait",localName="counter_wait",id="_FSM_fight_counter_wait",type="state"};
["fight.attacking.attack_return"]={name="fight.attacking.attack_return",localName="attack_return",id="_FSM_fight_attacking_attack_return",type="state"};
["fight.wait"]={name="fight.wait",localName="wait",id="_FSM_fight_wait",type="state"};
["fight.defense_stop"]={name="fight.defense_stop",localName="defense_stop",id="_FSM_fight_defense_stop",type="state"};
["start"]={name="start",localName="start",id="_FSM_start",type="state"};
["fight.defense_hold"]={name="fight.defense_hold",localName="defense_hold",id="_FSM_fight_defense_hold",type="state"};
["fight.counter_fail"]={name="fight.counter_fail",localName="counter_fail",id="_FSM_fight_counter_fail",type="state"};
["begin"]={name="begin",localName="begin",id="_FSM_begin",type="state"};
["begin_raise"]={name="begin_raise",localName="begin_raise",id="_FSM_begin_raise",type="state"};
["fight.attacking.attack_action"]={name="fight.attacking.attack_action",localName="attack_action",id="_FSM_fight_attacking_attack_action",type="state"};
["fight.gun_attack"]={name="fight.gun_attack",localName="gun_attack",id="_FSM_fight_gun_attack",type="state"};
["fight.defense_release"]={name="fight.defense_release",localName="defense_release",id="_FSM_fight_defense_release",type="state"};
["fight.attacking.attack_cancel"]={name="fight.attacking.attack_cancel",localName="attack_cancel",id="_FSM_fight_attacking_attack_cancel",type="state"};
["fight.start"]={name="fight.start",localName="start",id="_FSM_fight_start",type="state"};
["normal.start"]={name="normal.start",localName="start",id="_FSM_normal_start",type="state"};
["walk_in"]={name="walk_in",localName="walk_in",id="_FSM_walk_in",type="state"};
["fight.gun_failed"]={name="fight.gun_failed",localName="gun_failed",id="_FSM_fight_gun_failed",type="state"};
["win.stop"]={name="win.stop",localName="stop",id="_FSM_win_stop",type="state"};
["win"]={name="win",localName="win",id="_FSM_win",type="group"};
["fight.long_charge_execute"]={name="fight.long_charge_execute",localName="long_charge_execute",id="_FSM_fight_long_charge_execute",type="state"};
["fight.defense"]={name="fight.defense",localName="defense",id="_FSM_fight_defense",type="state"};
["normal.walk"]={name="normal.walk",localName="walk",id="_FSM_normal_walk",type="state"};
["normal"]={name="normal",localName="normal",id="_FSM_normal",type="group"};
["fight.gun_aim"]={name="fight.gun_aim",localName="gun_aim",id="_FSM_fight_gun_aim",type="state"};
["fight.long_charge"]={name="fight.long_charge",localName="long_charge",id="_FSM_fight_long_charge",type="state"};
["fight.attacking"]={name="fight.attacking",localName="attacking",id="_FSM_fight_attacking",type="group"};
["fight.attacking.attack_stop"]={name="fight.attacking.attack_stop",localName="attack_stop",id="_FSM_fight_attacking_attack_stop",type="state"};
["fight"]={name="fight",localName="fight",id="_FSM_fight",type="group"};
["fight.attacking.attack"]={name="fight.attacking.attack",localName="attack",id="_FSM_fight_attacking_attack",type="state"};
["dead"]={name="dead",localName="dead",id="_FSM_dead",type="state"};
["fight.gun_cancel"]={name="fight.gun_cancel",localName="gun_cancel",id="_FSM_fight_gun_cancel",type="state"};
["fight.long_charge_stop"]={name="fight.long_charge_stop",localName="long_charge_stop",id="_FSM_fight_long_charge_stop",type="state"};
["fight.defense_start"]={name="fight.defense_start",localName="defense_start",id="_FSM_fight_defense_start",type="state"};
["normal.walk_stopping"]={name="normal.walk_stopping",localName="walk_stopping",id="_FSM_normal_walk_stopping",type="state"};
["fight.counter"]={name="fight.counter",localName="counter",id="_FSM_fight_counter",type="state"};
};
-----------
nodelist["normal.encounter"].jump={
	["fight.start"]={ "_FSM_normal__jumpout","_FSM_fight__jumpin","fight.start" };
	["die"]={ "_FSM_normal__jumpout","dead" };
}
-----------
nodelist["fight.gun_attack_stop"].jump={
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
}
nodelist["fight.gun_attack_stop"].next={
["$wait"]="fight.wait";
[true]="fight.wait";
}
-----------
nodelist["normal.pre_encounter"].jump={
	["fight.start"]={ "_FSM_normal__jumpout","_FSM_fight__jumpin","fight.start" };
	["walk.step"]="normal.walk_stopping";
	["die"]={ "_FSM_normal__jumpout","dead" };
}
-----------
nodelist["fight.attacking.attack_start"].jump={
	["attack.approach"]="fight.attacking.attack_approach";
	["attack.execute"]="fight.attacking.attack";
	["attack.cancel"]="fight.attacking.attack_cancel";
	["fight.win"]={ "_FSM_fight_attacking__jumpout","_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight_attacking__jumpout","_FSM_fight__jumpout","dead" };
}
-----------
nodelist["win.start"].jump=false
nodelist["win.start"].next={
["$prize"]="win.prize";
[true]="win.prize";
}
-----------
nodelist["fight.charge"].jump={
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
}
nodelist["fight.charge"].next={
["$wait"]="fight.wait";
[true]="fight.wait";
}
-----------
nodelist["fight.attacking.attack_approach"].jump={
	["fight.win"]={ "_FSM_fight_attacking__jumpout","_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["attack.action"]="fight.attacking.attack_action";
	["die"]={ "_FSM_fight_attacking__jumpout","_FSM_fight__jumpout","dead" };
	["attack.execute"]="fight.attacking.attack";
}
-----------
nodelist["fight.gun_start"].jump={
	["gun.cancel"]="fight.gun_cancel";
	["gun.aim"]="fight.gun_aim";
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
	["gun.fail"]="fight.gun_failed";
}
-----------
nodelist["win.prize"].jump=false
nodelist["win.prize"].next={
["$stop"]="win.stop";
[true]="win.stop";
}
-----------
nodelist["fight.long_charge_release"].jump={
	["long_charge.stop"]="fight.long_charge_stop";
	["long_charge.execute"]="fight.long_charge_execute";
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
}
-----------
nodelist["fight.counter_wait"].jump={
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
	["defense.stop"]="fight.counter_fail";
	["counter.start"]="fight.counter";
}
-----------
nodelist["fight.attacking.attack_return"].jump={
	["attack.returned"]={ "_FSM_fight_attacking__jumpout","fight.wait" };
	["fight.win"]={ "_FSM_fight_attacking__jumpout","_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight_attacking__jumpout","_FSM_fight__jumpout","dead" };
}
-----------
nodelist["fight.wait"].jump={
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["order.charge"]="fight.charge";
	["order.gun"]="fight.gun_start";
	["die"]={ "_FSM_fight__jumpout","dead" };
	["order.attack"]={ "_FSM_fight_attacking__jumpin","fight.attacking.attack_start" };
	["order.defense_start"]="fight.defense_start";
	["order.long_charge"]="fight.long_charge";
}
-----------
nodelist["fight.defense_stop"].jump={
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
}
nodelist["fight.defense_stop"].next={
["$wait"]="fight.wait";
[true]="fight.wait";
}
-----------
nodelist["start"].jump={
	["scene.start"]="walk_in";
}
-----------
nodelist["fight.defense_hold"].jump={
	["order.defense_stop"]="fight.defense_release";
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
}
nodelist["fight.defense_hold"].next={
["$defense"]="fight.defense";
[true]="fight.defense";
}
-----------
nodelist["fight.counter_fail"].jump={
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["order.attack"]={ "_FSM_fight_attacking__jumpin","fight.attacking.attack_start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
}
-----------
nodelist["begin"].jump={
	["begin.stop"]={ "_FSM_normal__jumpin","normal.start" };
	["begin.raise"]="begin_raise";
}
-----------
nodelist["begin_raise"].jump=false
nodelist["begin_raise"].next={
["$begin"]="begin";
[true]="begin";
}
-----------
nodelist["fight.attacking.attack_action"].jump={
	["fight.win"]={ "_FSM_fight_attacking__jumpout","_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight_attacking__jumpout","_FSM_fight__jumpout","dead" };
	["attack.execute"]="fight.attacking.attack";
}
-----------
nodelist["fight.gun_attack"].jump={
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
	["gun.stop"]="fight.gun_attack_stop";
	["gun.fire"]="fight.gun_attack";
}
-----------
nodelist["fight.defense_release"].jump={
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
	["order.counter_wait"]="fight.counter_wait";
	["defense.stop"]="fight.defense_stop";
}
-----------
nodelist["fight.attacking.attack_cancel"].jump={
	["fight.win"]={ "_FSM_fight_attacking__jumpout","_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight_attacking__jumpout","_FSM_fight__jumpout","dead" };
}
nodelist["fight.attacking.attack_cancel"].next={
["$attack_return"]="fight.attacking.attack_return";
[true]="fight.attacking.attack_return";
}
-----------
nodelist["fight.start"].jump={
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
}
nodelist["fight.start"].next={
["$wait"]="fight.wait";
[true]="fight.wait";
}
-----------
nodelist["normal.start"].jump={
	["fight.start"]={ "_FSM_normal__jumpout","_FSM_fight__jumpin","fight.start" };
	["die"]={ "_FSM_normal__jumpout","dead" };
}
nodelist["normal.start"].next={
["$walk"]="normal.walk";
[true]="normal.walk";
}
-----------
nodelist["walk_in"].jump=false
nodelist["walk_in"].next={
["$begin"]="begin";
[true]="begin";
}
-----------
nodelist["fight.gun_failed"].jump={
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
}
nodelist["fight.gun_failed"].next={
["$wait"]="fight.wait";
[true]="fight.wait";
}
-----------
nodelist["win.stop"].jump=false
nodelist["win.stop"].next={
["$normal"]={ "_FSM_win__jumpout","_FSM_normal__jumpin","normal.start" };
[true]={ "_FSM_win__jumpout","_FSM_normal__jumpin","normal.start" };
}
-----------
nodelist["win"].jump=false
-----------
nodelist["fight.long_charge_execute"].jump={
	["long_charge.stop"]="fight.long_charge_stop";
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
}
-----------
nodelist["fight.defense"].jump={
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["order.defense_stop"]="fight.defense_release";
	["defense.hold"]="fight.defense_hold";
	["die"]={ "_FSM_fight__jumpout","dead" };
}
-----------
nodelist["normal.walk"].jump={
	["fight.start"]={ "_FSM_normal__jumpout","_FSM_fight__jumpin","fight.start" };
	["enemy.encounter"]="normal.pre_encounter";
	["die"]={ "_FSM_normal__jumpout","dead" };
}
-----------
nodelist["normal"].jump={
	["fight.start"]={ "_FSM_fight__jumpin","fight.start" };
	["die"]="dead";
}
-----------
nodelist["fight.gun_aim"].jump={
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
	["gun.fire"]="fight.gun_attack";
}
-----------
nodelist["fight.long_charge"].jump={
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["order.long_charge_stop"]="fight.long_charge_release";
	["die"]={ "_FSM_fight__jumpout","dead" };
}
-----------
nodelist["fight.attacking"].jump={
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
}
-----------
nodelist["fight.attacking.attack_stop"].jump={
	["die"]={ "_FSM_fight_attacking__jumpout","_FSM_fight__jumpout","dead" };
	["attack.returned"]={ "_FSM_fight_attacking__jumpout","fight.wait" };
	["fight.win"]={ "_FSM_fight_attacking__jumpout","_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["attack.return"]="fight.attacking.attack_return";
}
-----------
nodelist["fight"].jump={
	["die"]="dead";
	["fight.win"]={ "_FSM_win__jumpin","win.start" };
}
-----------
nodelist["fight.attacking.attack"].jump={
	["attack.execute"]="fight.attacking.attack";
	["attack.cancel"]="fight.attacking.attack_cancel";
	["fight.win"]={ "_FSM_fight_attacking__jumpout","_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["attack.stop"]="fight.attacking.attack_stop";
	["die"]={ "_FSM_fight_attacking__jumpout","_FSM_fight__jumpout","dead" };
}
-----------
nodelist["dead"].jump=false
-----------
nodelist["fight.gun_cancel"].jump={
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
}
nodelist["fight.gun_cancel"].next={
["$gun_attack_stop"]="fight.gun_attack_stop";
[true]="fight.gun_attack_stop";
}
-----------
nodelist["fight.long_charge_stop"].jump={
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
}
nodelist["fight.long_charge_stop"].next={
["$wait"]="fight.wait";
[true]="fight.wait";
}
-----------
nodelist["fight.defense_start"].jump={
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["order.defense_stop"]="fight.defense_release";
	["defense.ready"]="fight.defense";
	["die"]={ "_FSM_fight__jumpout","dead" };
}
-----------
nodelist["normal.walk_stopping"].jump={
	["fight.start"]={ "_FSM_normal__jumpout","_FSM_fight__jumpin","fight.start" };
	["walk.stop"]="normal.encounter";
	["die"]={ "_FSM_normal__jumpout","dead" };
}
-----------
nodelist["fight.counter"].jump={
	["attack.approach"]={ "_FSM_fight_attacking__jumpin","fight.attacking.attack_approach" };
	["fight.win"]={ "_FSM_fight__jumpout","_FSM_win__jumpin","win.start" };
	["die"]={ "_FSM_fight__jumpout","dead" };
}
return nodelist
end) ()

