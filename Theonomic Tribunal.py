#If replit starts to complain that things are missing from discord2
#and it's only using the "discord" package (which has the same import namespace)
#fix imports like this:
# - let it install discord
# - run this: pip install --upgrade --no-deps --force-reinstall git+https://github.com/Pycord-Development/pycord

#-----notes about slash commands:-----
# we are using this library: https://github.com/Pycord-Development/pycord
# after the decorator @bot.slash_command(guild_ids = guild_ids)...
# the function header should look like this:
# async def COMMAND_NAME(ctx, ......)
#
# in the ....... space, put the arguments for the command, which should look like this:
# ARGUMENT_NAME: discord.Option(str, "a description of the argument")
#
#the "str" part can be repaced with "int" or whatever other type is expected.


import discord
#import discord.Option
#import discord.Bot
#import discord.AutocompleteContext


from replit import db
import string
import os
import time
from datetime import datetime
from Court import case, namecombodb1, namecombodb2, namecombodb3, lutherinsults, accusationdroptime, trialrecordtime, judicialpenalties, penaltyList
import random
import asyncio


guild_ids= [123456789123456789]

token = 'TOP_SECRET_TOKEN' #token for bot to join discord


#-----VARIABLES
#-------Dictionary Stuff
termList = []
#-------Court Stuff
caselist = []
db_caselist_key = 0 #int; stored in db to show what the most recent caselist update prefix was. Read this from db and delete
prefix = "/"

def first(iterable, default=None):
  for item in iterable:
    return item
  return default



#---------------Beginning of Async (bot, slash relevant) stuff

#idk if these intents work anymore, but they were needed for some of the tribunal court stuff
intents = discord.Intents(messages=True, guilds=True, members = True)
intents.members = True

bot = discord.Bot(intents = intents)

#-----------------------------------
#--------------Court bot stuff
#-----------------------------------
  
#--------------Special functions to be called from bot commands
async def serializeCaseList():	
	#serialize and dump caselist into the db
	#delete previous caselist db

  #if this is the first time running, there'll be no caselist key. Initialize it.
  db_caselist_key = 0
  keymatch = db.prefix("db_caselist_key") #list all keys which match a prefix
  if len(keymatch) == 0:
    db["db_caselist_key"] = db_caselist_key
  db_caselist_key = int(db["db_caselist_key"])

	#all the cases in the new list will have an updated key so we can differentiate them from the old list
	#this way we can delete the old case list from the db after we insert the new one
	#this is intended to prevent scenarios where the server resets in the middle of an update and the whole db is lost
  if (db_caselist_key >= 7):
    newkey = 0
  else:
    newkey = db_caselist_key + 1 
	
  sCaseList = []
  thiscaseentryid = 0
  print("serializing...")
  #serialize the case list
  for item in caselist:
    caseprefix = "case " + str(newkey) + " " + str(thiscaseentryid) + " "
    sCaseList.append([caseprefix + "caseid", str(item.caseid)]) #int
    sCaseList.append([caseprefix + "activetrial", str(item.activetrial)]) #bool
    sCaseList.append([caseprefix + "completetrial", str(item.completetrial)]) #bool
    sCaseList.append([caseprefix + "penaltypending", str(item.penaltypending)]) #bool
    #print(str(item.defendant))
    if (item.defendant == None):
      sCaseList.append([caseprefix + "defendant", None]) #discord.Member
    else:
      #print("the actual defendant user is going into the list")
      #print(str(item.defendant))
      sCaseList.append([caseprefix + "defendant", str(item.defendant)]) #discord.Member
    #print(str(item.accuser))
    sCaseList.append([caseprefix + "accuser", str(item.accuser)]) #discord.Member
    sCaseList.append([caseprefix + "accusationtime", str(item.accusationtime)]) #python datetime
    sCaseList.append([caseprefix + "trialendtime", str(item.trialendtime)]) #pytho    datetime
    sCaseList.append([caseprefix + "deferredpenalty", str(item.deferredpenalty)]) #bool
    sCaseList.append([caseprefix + "penaltyid", str(item.penaltyid)]) #int
    if item.judge != None:
      sCaseList.append([caseprefix + "judge", str(item.judge)]) #discord.Member
    else:
      sCaseList.append([caseprefix + "judge", None])
    sCaseList.append([caseprefix + "witnessqty", str(item.witnessqty)]) #int
    thisrecordid = 0
    for record in item.record:
      sCaseList.append([caseprefix + "recordtype " + format(thisrecordid, '04d'), record[0]])
      sCaseList.append([caseprefix + "record " + format(thisrecordid, '04d'), record[1]])
      thisrecordid += 1
    thiscaseentryid += 1
	
	#dump the case list into the db 
  for item in sCaseList:
    db[item[0]] = item[1]
    #print("{}: {}".format(item[0],item[1]))
	
  #delete the old caselist
  oldCaseList = db.prefix("case " + str(db_caselist_key))
  for key in oldCaseList:
  	del db[key]

  #it's possible that the old caselist will have been only partially deleted in a past  update. clean it up now.
  oldCaseList = db.prefix("case " + str(db_caselist_key - 1))
  for key in oldCaseList:
  	del db[key]

  #we don't want to have a giant integer eating our memory.
  if (db_caselist_key >= 7):
  	db_caselist_key = 0
  else:
  	db_caselist_key += 1
  db["db_caselist_key"] = db_caselist_key
  print("...done")

async def deserializeCaseList():
  #read caselist from database
  caselist.clear();
	#if this is the first time running, there'll be no caselist key. Initialize it.
  db_caselist_key = 0
  keymatch = db.prefix("db_caselist_key") #list all keys which match a prefix
  if len(keymatch) == 0:
  	db["db_caselist_key"] = db_caselist_key
  db_caselist_key = int(db["db_caselist_key"])

  thiscaseentryid = 0
  caseprefix = "case " + str(db_caselist_key) + " " + str(thiscaseentryid) + " "
  dbentries = db.prefix(caseprefix)
  while len(dbentries) > 0:
    mycaseid		 = int(db[caseprefix + "caseid"]) #int
    myactivetrial	 = bool((db[caseprefix + "activetrial"] == 'True') or (db[caseprefix + "activetrial"] == '1')) #bool
    mycompletetrial	 = bool((db[caseprefix + "completetrial"] == 'True') or (db[caseprefix + "completetrial"] == '1')) #bool
    mypenaltypending = bool((db[caseprefix + "penaltypending"] == 'True') or (db[caseprefix + "penaltypending"] == '1')) #bool
    mydefendant		 = db[caseprefix + "defendant"]#discord.Member
    myaccuser		 = db[caseprefix + "accuser"] #discord.Member
    #print(int(db[caseprefix + "defendant"]))
   # print(int(db[caseprefix + "defendant"]))
    myaccusationtime = datetime.strptime(db[caseprefix + "accusationtime"], '%Y-%m-%d %H:%M:%S.%f') #python datetime
    if (db[caseprefix + "trialendtime"] == None) or (db[caseprefix + "trialendtime"] == 'None'):
      mytrialendtime = None
    else:
      mytrialendtime = datetime.strptime(db[caseprefix + "trialendtime"], '%Y-%m-%d %H:%M:%S.%f') #python datetime
    mydeferredpenalty = bool((db[caseprefix + "deferredpenalty"] == 'True') or (db[caseprefix + "deferredpenalty"] == '1')) #bool
    mypenaltyid		 = db[caseprefix + "penaltyid"] #int
    if (db[caseprefix + "judge"] == None) or (db[caseprefix + "judge"] == 'None'):
      myjudge = None
    else:
      myjudge			 = db[caseprefix + "judge"] #discord.Member
    mywitnessqty	 = int(db[caseprefix + "witnessqty"]) #int
		
    mycase = case(mycaseid, myactivetrial, mycompletetrial, mypenaltypending, mydefendant, myaccuser, myaccusationtime, mytrialendtime, [], mydeferredpenalty, mypenaltyid, myjudge, mywitnessqty)
    recordtypelist = db.prefix(caseprefix + "recordtype ")
    recordlist = db.prefix(caseprefix + "record ")
    for p in range(len(recordlist)):
      mycase.record.append((db[recordtypelist[p]], db[recordlist[p]]))
    caselist.append(mycase)
		
    thiscaseentryid += 1
    caseprefix = "case " + str(db_caselist_key) + " " + str(thiscaseentryid) + " "
    dbentries = db.prefix(caseprefix)
		
    if (thiscaseentryid > 1000):
      print("caselist overflow in deserializeCaseList()\n")
      break
  
  if (len(caselist) > 0):
    print("deserialization successful\n")
  else:
    print("deserialization unsuccessful\n")
  #caselist = localcaselist

async def caseUpdateCheck(caseID):
    #await deserializeCaseList()
    #searches for the caseID and removes it from the caselist if it's expired. Returns its index if found and not expired, or -1 otherwise.
    now = datetime.now()
    i = -1
    m = False
    for x in caselist:
        i += 1
        if int(x.caseid) == int(caseID):
            m = True
            break
    #i, x = first((i,x) for i,x in enumerate(caselist) if x.caseid == caseID)
    if (m == False): #if there is no case matching that case ID
        return -1
    else:
        if ((not x.activetrial) and (not x.completetrial)): #if the case hasn't yet been brought to trial
            if (len([item for item in x.record if item[0] == 1]) < 2): #if there is less than 2 lines of witness
                if (((now-x.accusationtime).total_seconds()/60) > accusationdroptime): #if the accusation is expired
                    print("accusation expired\n")
                    del caselist[i] #delete the case from the record
                    await serializeCaseList()
                    return -1
            if (x.completetrial): #if the trial is complete
                if (((now-x.trialendtime).total_seconds()/60) > trialrecordtime): #if the case is expired
                    print ("case expired")
                    del caselist[i]#delete the case from the record
                    await serializeCaseList()
                    return -1
    #await serializeCaseList()
    return i


async def caseListCleanup():
    await deserializeCaseList()
    #if (len(caselist) > 0):
    #  print("deserialization successful\n")
    #else:
    #  print("deserialization unsuccessful\n")
    #updates the case record by removing cases according to the time limits: accusationdroptime and trialrecordtime
    now = datetime.now()
    i = -1
    for x in caselist:
        i += 1
        if ((not x.activetrial) and (not x.completetrial)): #trial not started
            if (len([item for item in x.record if item[0] == 1]) < 2): #less than 2 witnesses
                if (((now-x.accusationtime).total_seconds()/60) > accusationdroptime):
                    print("deleting expired case")
                    del caselist[i]
        if (x.completetrial and (x.trialendtime != None)): #trial completed
            if (((now-x.trialendtime).total_seconds()/60) > trialrecordtime):
                print("deleting expired record")
                del caselist[i]

    await serializeCaseList()


async def tempmute(targetUser, minutes, ctx):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    await targetUser.add_roles(muted_role,reason = "Penalty for crimes.")
    if (minutes > 0):
        await asyncio.sleep(minutes * 60)
        await targetUser.remove_roles(muted_role, reason = "time's up")
        await ctx.send("{} is unmuted.".format(targetUser.mention))


async def tempban(targetUser, minutes, ctx):
    #muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    await targetUser.ban(delete_message_days = 0)
    if (minutes > 0):
        await asyncio.sleep(minutes * 60)
        await targetUser.unban()
        await ctx.send("{} is unbanned.".format(targetUser.mention))

#penaltyList = ["Acquit", "Nick-Change", "Chastize", "Luther Chastize", "Minute Mute", "Hour Mute", "Kick", "Day Ban", "Permaban"]
async def doPenalty(ctx, target, penaltyID, modifier):
    print(target)
    targetUser = ctx.guild.get_member_named(str(target))
    if targetUser == None:
      ctx.respond("The defendant wasn't found in our guild. No penalty to perform.")
      return
    print(targetUser)
    #print("The penalty script is running with penaltyID " + str(penaltyID))
    if (penaltyID == "Acquit"): #Acquit: close the case; no other action.
        await ctx.respond("{} has been acquitted. The record is clean.".format(targetUser.mention))
    elif (penaltyID == "Nick-Change"): #nickchange: give a silly nick to the target user
        if ((modifier == "") or (modifier == None)):
            newname = namecombodb1[random.randrange(0,len(namecombodb1))] + namecombodb2[random.randrange(0,len(namecombodb2))] + namecombodb3[random.randrange(0,len(namecombodb3))]
        else:
            newname = modifier
        oldname = targetUser.name
        await targetUser.edit(nick = newname)
        await ctx.respond("{} shall hereafter be known as {}. How shameful! {}".format(oldname, newname, targetUser.mention))
    elif (penaltyID == "Chastize"): #chastize: tell the target user not to do it again
        #print("did I make it here?")
        await ctx.respond("{}, what you did was wrong. Don't do it again.".format(targetUser.mention))
    elif (penaltyID == "Luther Chastize"): #lutherchastize: issue a lutheran insult
        mylist = list(lutherinsults.items())
        insult = "{}".format(targetUser.mention)
        insult += "```"+mylist[random.randrange(0,len(mylist))][1]+"``` *-"+mylist[random.randrange(0,len(mylist))][0] + "*"
        await ctx.respond(insult)
    elif (penaltyID == "Minute Mute"): #minutemute: mute the target user for 5 minutes
        await ctx.respond('{} is muted for 5 minutes.'.format(targetUser.mention))
        await tempmute(targetUser,5,ctx)
    elif (penaltyID == "Hour Mute"): #hourmute: mute target user for an hour
        await ctx.respond('{} is muted for an hour.'.format(targetUser.mention))
        await tempmute(targetUser,60,ctx)
    elif (penaltyID == "Kick"): #kick: kick target user
        if targetUser.guild_permissions.administrator:
            await ctx.respond("The user is an administrator, and must be kicked manually by another administrator.")
        else:
            await ctx.respond("{} is kicked.".format(targetUser.mention))
            await targetUser.kick()
    elif (penaltyID == "Day Ban"): #dayban: ban target user for a day
        if targetUser.guild_permissions.administrator:
            await ctx.respond("The user is an administrator, and must be banned manually by another administrator.")
        else:
            #try:
            await ctx.respond('{} is banned for the day.'.format(targetUser.mention))
            await tempban(targetUser,24*60,ctx)
                #ban_list.append(member)
                #ban_minute_.append(24*60*60)
                #ban_server_list.append(ctx.message.server)
            #except:
                #await ctx.respond('Error! User not active')
    elif (penaltyID == "Permaban"): #permaban: ban target user forever
        if targetUser.guild_permissions.administrator:
            await ctx.respond("The user is an administrator, and must be banned manually by another administrator.")
        else:
            try:
                await targetUser.ban(delete_message_days = 0)
                await ctx.respond('{} is banned.'.format(targetUser.mention))
            except:
                await ctx.respond('Error! User not active')



#-----------------------------------
#--------------Court Commands
#-----------------------------------
#--------------Citzen Connamds
# Citizens:
# - Accuse
# - TrialList
# - TrialRecord
# - Defense
# - Witness
# - Plea
# - Forgive
# - ForTheRecord
# - Execute

#____________Help_______________
@bot.slash_command(guild_ids = guild_ids, description = "Info about the bot.")
async def help(ctx):
  outstring = "The Tribunal Bot provides definitions for the roles in TQ&A, and keeps a record of mock trials.\nThese are the commands for **general use**:\n\n\
  `/define` - get the definition for a role.\n\n\
  `/triallist` - See a summary list of trials.\n\
  `/trialrecord` - See the full record for one trial.\n\
  `/accuse` - Initiate a case by accusing someone of a crime.\n\
  `/witness` - Submit evidence for an accusation. Only cases with two witnesses go to trial.\n\
  `/defense` - Submit defense for a trial.\n\
  `/fortherecord` - Make a note on a trial.\n\
  `/plea` - Defendant only: state innocent or guilty.\n\
  `/forgive` - Accuser only: delete the trial and accusation before penalty.\n\
  `/execute` - Accuser only: after penalty has been issued, cast the first stone."
  await ctx.respond(outstring); 
  role = discord.utils.get(ctx.guild.roles, name="Judge")
  if role in ctx.author.roles:
    outstring2 = "These are the commands for **judges**:\n\n\
  `/reject` - Delete an accusation before it goes to trial.\n\
  `/starttrial` - Accept a case and register yourself as the acting judge for it.\n\
  `/judge` - State guilty or innocent for the record (does not close the case).\n\
  `/consult` - Request help from other judges, or provide help to the acting judge.\n\
  `/penalize` - Finalize a case by deciding the penalty. The right to execute the penalty is deferred to the accuser by default, but can be set to trigger immediately by the judge.\n\
  `/penalties` - Show the list of penalties with some brief explanations."
    await ctx.respond(outstring2); 

              
#____________Accuse_______________
#Accuse creates a case object with the accuser, accused, and allegation. The case is inactive until a judge starts the trial.
@bot.slash_command(guild_ids = guild_ids, description = "Accuse someone of something. Case will be given an ID for reference.")
async def accuse(ctx, defendant: discord.Option(discord.Member, "User to be accused.", required = True), crime: discord.Option(str, "Crime they committed.", required = True)):
  if defendant: #the user field wasn't empty
    myID = 1
    if (len(caselist) > 0):
      myID = max(node.caseid for node in caselist) + 1
    else:
      myID = 1
    targetUser = ctx.guild.get_member_named(str(defendant))
    if targetUser:
      myrecordstring = "{} has accused {} with the following claim: ".format(ctx.author.mention, targetUser.mention)
    else:
      myrecordstring = "{} has accused {} with the following claim: ".format(ctx.author.mention, defendant)
    myrecordstring += crime
    mycase = case(myID, False, False, False, defendant, str(ctx.author), datetime.now(),None,[])
    mycase.record.append((1, myrecordstring))
    caselist.append(mycase)
    await ctx.respond(myrecordstring + "\nYour case ID is: " + str(myID))
  else:
    await ctx.respond("The second argument must mention a user."); 
  await serializeCaseList()

#____________TrialList_______________
#Outputs the list of past trials
@bot.slash_command(guild_ids = guild_ids, description = "View a record of past trials.")
async def triallist(ctx):
  outputstrings = ["Case ID, Accuser, Defendant, Accusation Date, Trial Started, Trial End Date, Result:\n"]
  n = 0
  if (len(caselist) > 0):
      for mycase in caselist:
          teststring = "→ {}, {}, {}, {}, {}, {}, ".format(mycase.caseid, mycase.accuser, mycase.defendant, mycase.accusationtime, mycase.activetrial, mycase.trialendtime)
          if (mycase.completetrial):
              teststring += "{}".format(mycase.record[-1][1])
          elif (mycase.activetrial):
              teststring += "Trial Ongoing"
          else:
              teststring += "Awaiting Trial"
          teststring += "\n"
          if (len(outputstrings[n] + teststring) >= 2000):
            outputstrings.append("")
            n += 1
            outputstrings[n] += teststring
          else:
            outputstrings[n] += teststring
  else:
     outputstrings[0] += "No Cases On Record"
  for result in outputstrings:
    await ctx.respond(result)
  #await serializeCaseList() #not necessary as no changes are made to caselist in this function

#____________TrialRecord_______________
@bot.slash_command(guild_ids = guild_ids, description = "View the full and detailed record for a specific trial.")
async def trialrecord(ctx, caseid: discord.Option(str, "Numeric ID from TrialList.", required = True)):
    #await deserializeCaseList()
    if (caseid == "0"): #valid caseID starts at 1
        await ctx.respond("You have to enter a caseID (a number, issued with your case. Maybe check the /triallist if you forgot)")
    else:
        caseindex = await caseUpdateCheck(caseid)
        if (caseindex == -1): 
            await ctx.respond("No such Case ID on record. Remember that completed cases and accusations without at least 2 witnesses are deleted from the record after a fixed time period.")
        else:
            mycase = caselist[caseindex]
            outputstrings = [""]
            
            outputstrings[0] = "Case ID, Accuser, Defendant, Accusation Date, Trial Started, Trial End Date\n"
            outputstrings[0] += "{}, {}, {}, {}, {}, {}\n".format(mycase.caseid, mycase.accuser, mycase.defendant, mycase.accusationtime, mycase.activetrial, mycase.trialendtime)

            
            outputstrings[0] += "\n*The Record:*\n"
            n = 0
            for record in caselist[caseindex].record:
              if (len(outputstrings[n] + "→ " + record[1] + "\n") >= 2000):
                outputstrings.append("")
                n += 1
                outputstrings[n] += "→ " + record[1] + "\n"
              else:
                outputstrings[n] += "→ " + record[1] + "\n"
            for result in outputstrings:
              await ctx.respond(result)
    await serializeCaseList()

#____________Defense_______________
@bot.slash_command(guild_ids = guild_ids, description = "Submit evidence in defense for a case.")
async def defense(ctx, caseid: discord.Option(str, "Numeric ID from TrialList.", required = True), evidence: discord.Option(str, "Evidence for the defense.", required = True)):
    #await deserializeCaseList()
    if (caseid == "0"): #valid caseID starts at 1
        await ctx.respond("You have to enter a caseID (a number, issued with your case. Maybe check the /triallist if you forgot)")
    else:
        if (not caseid.isnumeric()):
            await ctx.respond("invalid case ID")
        else:
            caseindex = await caseUpdateCheck(caseid)
            if (caseindex == -1): 
                await ctx.respond("No such Case ID on record. Remember that completed cases and accusations without at least 2 witnesses are deleted from the record after a fixed time period.")
            else:
                if (caselist[caseindex].completetrial):
                    await ctx.respond("("+caseid+")The case in question is closed. No new records will be accepted.")
                else:
                    outputstring = "({}){} submits for defense: ".format(caseid, str(ctx.author))
                    outputstring += evidence
                    caselist[caseindex].record.append((3, outputstring))
                    await ctx.respond(outputstring)
                    await serializeCaseList()

                  
#____________ witness _______________
@bot.slash_command(guild_ids = guild_ids, description = "Present evidence in support of an accusation.")
async def witness(ctx, caseid: discord.Option(str, "Numeric ID from TrialList.", required = True), evidence: discord.Option(str, "Evidence for prosecution.", required = True)):
    #await deserializeCaseList()
    if (caseid == "0"): #valid caseID starts at 1
        await ctx.respond("You have to enter a caseID (a number, issued with your case. Maybe check the /triallist if you forgot)")
    else:
        if (not caseid.isnumeric()):
            await ctx.respond("invalid case ID")
        else:
            caseindex = await caseUpdateCheck(caseid)
            if (caseindex == -1): 
                await ctx.respond("No such Case ID on record. Remember that completed cases and accusations without at least 2 witnesses are deleted from the record after a fixed time period. See "+prefix+"help");
            else:
                if (caselist[caseindex].completetrial):
                    await ctx.respond("("+caseid+")The case in question is closed. No new records will be accepted.")
                else:
                    outputstring = "({}){} submits for witness: ".format(caseid, str(ctx.author))
                    outputstring += evidence
                    caselist[caseindex].record.append((1, outputstring))
                    caselist[caseindex].witnessqty += 1
                    await ctx.respond(outputstring)
    await serializeCaseList()

#____________ plea _______________
@bot.slash_command(guild_ids = guild_ids, description = "For an accused person, state whether you are guilty or innocent.")
async def plea(ctx, caseid: discord.Option(str, "Numeric ID from TrialList.", required = True), pleacontent: discord.Option(str, "Guilty or Innocent.", required = True)):
    #await deserializeCaseList()
    if (caseid == "0"): #valid caseid starts at 1
        await ctx.respond("You have to enter a caseID (a number, issued with your case. Maybe check the /triallist if you forgot)")
    else:
        if (not caseid.isnumeric()):
            await ctx.respond("invalid case ID")
        else:
            caseindex = await caseUpdateCheck(caseid)
            if (caseindex == -1): 
                await ctx.respond("No such Case ID on record. Remember that completed cases and accusations without at least 2 witnesses are deleted from the record after a fixed time period.");
            else:
                if (caselist[caseindex].completetrial):
                    await ctx.respond("("+caseid+")The case in question is closed. No new records will be accepted.")
                else:
                    if (str(caselist[caseindex].defendant) == str(ctx.author)):
                        outputstring = "({}){} pleas: ".format(caseid, str(ctx.author))
                        outputstring += pleacontent
                        caselist[caseindex].record.append((2, outputstring))
                        await ctx.respond(outputstring)
                    else:
                        #print(caselist[caseindex].defendant)
                        #print(str(ctx.author))
                        await ctx.respond("Only the defendant may plea.")
    await serializeCaseList()

  
#Erases an accusation and terminates associated trials. Only the accuser may forgive. Format:\n```"+prefix+"forgive [case ID]```  
#____________ forgive _______________
@bot.slash_command(guild_ids = guild_ids, description = "Erases an accusation and terminates associated trial. Only the accuser may forgive.")
async def forgive(ctx, caseid: discord.Option(str, "Numeric ID from TrialList.", required = True)):
    #await deserializeCaseList()
    if (caseid == "0"): #valid caseID starts at 1
        await ctx.respond("You have to enter a caseID (a number, issued with your case. Maybe check the /triallist if you forgot)")
    else:
        if (not caseid.isnumeric()):
            await ctx.respond("invalid case ID")
        else:
            caseindex = await caseUpdateCheck(caseid)
            if (caseindex == -1): 
                await ctx.respond("No such Case ID on record. Remember that completed cases and accusations without at least 2 witnesses are deleted from the record after a fixed time period.");
            else:
                if (caselist[caseindex].completetrial):
                    await ctx.respond("("+caseid+")The case in question is closed. No new records will be accepted.")
                else:
                    #print(str(caselist[caseindex].accuser) + "\n" + str(ctx.author))
                    if (caselist[caseindex].accuser == str(ctx.author)):
                        targetUser = ctx.guild.get_member_named(str(caselist[caseindex].defendant))
                        if targetUser:
                          outputstring = "({}){} has decided to forgive {}. The case is closed.".format(caseid, str(ctx.author), targetUser.mention)
                        else:
                          outputstring = "({}){} has decided to forgive {}. The case is closed.".format(caseid, str(ctx.author), str(caselist[caseindex].defendant))
                        await ctx.respond(outputstring)
                        del caselist[caseindex]
                        #caselist[caseindex].completetrial = True
                        #caselist[caseindex].activetrial = False
                        #caselist[caseindex].trialendtime = datetime.now()
                        #caselist[caseindex].record.append((4, outputstring))
                    else:
                        await ctx.respond("Only the accuser may forgive.")
    await serializeCaseList()


#____________ fortherecord _______________
@bot.slash_command(guild_ids = guild_ids, description = "Submit a general statement to be kept in the trial record for a specific case.")
async def fortherecord(ctx, caseid: discord.Option(str, "Numeric ID from TrialList.", required = True), recordadd: discord.Option(str, "Comments.", required = True)):
    #await deserializeCaseList()
    if (caseid == "0"): #valid caseID starts at 1
        await ctx.respond("You have to enter a caseID (a number, issued with your case. Maybe check the /triallist if you forgot)")
    else:
        if (not caseid.isnumeric()):
            await ctx.respond("invalid case ID")
        else:
            caseindex = await caseUpdateCheck(caseid)
            if (caseindex == -1): 
                await ctx.respond("No such Case ID on record. Remember that completed cases and accusations without at least 2 witnesses are deleted from the record after a fixed time period.");
            else:
                if (caselist[caseindex].completetrial):
                    await ctx.respond("("+caseid+")The case in question is closed. No new records will be accepted.")
                else:
                    outputstring = "({}){} submits for the record: ".format(caseid, str(ctx.author))
                    outputstring += recordadd
                    caselist[caseindex].record.append((5, outputstring))
                    await ctx.respond(outputstring)
					
    await serializeCaseList()

#____________ execute _______________
@bot.slash_command(guild_ids = guild_ids, description = "Execute penalty if deferred to accuser by the judge.")
async def execute(ctx, caseid: discord.Option(str, "Numeric ID from TrialList.", required = True), penaltyarg: discord.Option(str, "Argument for the penalty (e.g. silly name).", default = "", required = False)):
    #await deserializeCaseList()
    if (caseid == "0"): #valid caseID starts at 1
        await ctx.respond("You have to enter a caseID (a number, issued with your case. Maybe check the /triallist if you forgot)")
    else:
        if (not caseid.isnumeric()):
            await ctx.respond("Invalid case ID")
        else:
            caseindex = await caseUpdateCheck(caseid)
            if (caseindex == -1): 
                await ctx.respond("No such Case ID on record. Remember that completed cases and accusations without at least 2 witnesses are deleted from the record after a fixed time period.");
            else:
                if (caselist[caseindex].completetrial or (not caselist[caseindex].activetrial)):
                    await ctx.respond("("+caseid+")You can only penalize for cases which are actively in trial")
                else:
                    if (caselist[caseindex].accuser == str(ctx.author)):
                        if (caselist[caseindex].deferredpenalty == True):
                            outputstring = "("+caseid+")The accuser has executed his right to penalize the defendant. The penalty is: "
                            outputstring += caselist[caseindex].penaltyid
                            modifier = ""
                            if (len(penaltyarg) > 0):
                              modifier += penaltyarg
                              #modifier = modifier[:-1]
                            await doPenalty(ctx, caselist[caseindex].defendant, caselist[caseindex].penaltyid, modifier)
                            caselist[caseindex].completetrial = True
                            caselist[caseindex].activetrial = False
                            caselist[caseindex].trialendtime = datetime.now()
                            caselist[caseindex].record.append((10, outputstring))
                            await ctx.respond(outputstring)
                        else:
                            await ctx.respond("\nThe right to issue a penalty has not been delegated to the accuser.")
                    else:
                        await ctx.respond("Only the accuser may execute the penalty.")
    await serializeCaseList()

#--------------Judge Connamds
# Judges: if ctx.author.guild_permissions.administrator:
# - Reject
#____________ Reject _______________
@bot.slash_command(guild_ids = guild_ids, description = "JUDGE ONLY: Reject and delete a case before it goes to trial.")
async def reject(ctx, caseid: discord.Option(str, "Numeric ID from TrialList.", required = True)):
    #await deserializeCaseList()
    if (caseid == "0"): #valid caseID starts at 1
        await ctx.respond("You have to enter a caseID (a number, issued with your case. Maybe check the /triallist if you forgot)")
    else:
        role = discord.utils.get(ctx.guild.roles, name="Judge")
        if role in ctx.author.roles:
            if (not caseid.isnumeric()):
                await ctx.respond("invalid case ID")
            else:
                caseindex = await caseUpdateCheck(caseid)
                if (caseindex == -1): 
                    await ctx.respond("No such Case ID on record. Remember that completed cases and accusations without at least 2 witnesses are deleted from the record after a fixed time period.");
                else:
                    if (caselist[caseindex].completetrial or caselist[caseindex].activetrial):
                        await ctx.respond("("+caseid+")A case can only be rejected before it goes to trial.")
                    else:
                        outputstring = "("+caseid+")The accusation has been rejected. The case is removed from the record."
                        del caselist[caseindex]
                        await ctx.respond(outputstring)
        else:
            await ctx.respond("You do not have the required role to perform this command.")
    await serializeCaseList()
# - StartTrial
#____________ starttrial _______________
@bot.slash_command(guild_ids = guild_ids, description = "JUDGE ONLY: Accept and adjudicate a case.")
async def starttrial(ctx, caseid: discord.Option(str, "Numeric ID from TrialList.", required = True)):
    #await deserializeCaseList()
    if (caseid == "0"): #valid caseID starts at 1
        await ctx.respond("You have to enter a caseID (a number, issued with your case. Maybe check the /triallist if you forgot)")
    else:
        role = discord.utils.get(ctx.guild.roles, name="Judge")
        if role in ctx.author.roles:
            if (not caseid.isnumeric()):
                await ctx.respond("invalid case ID")
            else:
                caseindex = await caseUpdateCheck(caseid)
                if (caseindex == -1): 
                    await ctx.respond("No such Case ID on record. Remember that completed cases and accusations without at least 2 witnesses are deleted from the record after a fixed time period.");
                else:
                    if (caselist[caseindex].completetrial or caselist[caseindex].activetrial):
                        await ctx.respond("("+caseid+")The case was already started.")
                    else:
                        if (caselist[caseindex].witnessqty < 2):
                            await ctx.respond("("+caseid+")A case cannot be started without at least 2 lines of witness.")
                        else:
                            outputstring = "({})Court is now in session. Honorable Judge {} presiding over trial {}.".format(caseid, str(ctx.author), str(caseid))
                            caselist[caseindex].record.append((7, outputstring))
                            caselist[caseindex].activetrial = True
                            caselist[caseindex].judge = str(ctx.author)
                            await ctx.respond(outputstring)
        else:
            await ctx.respond("You do not have the required role to perform this command.")
    await serializeCaseList()

  
# - Judge
#____________ judge _______________
@bot.slash_command(guild_ids = guild_ids, description = "JUDGE ONLY: State innocent or guilty for the record.")
async def judge(ctx, caseid: discord.Option(str, "Numeric ID from TrialList.", required = True), verdict: discord.Option(str, "Innocent or Guilty.", required = True)):
    #await deserializeCaseList()
    if (caseid == "0"): #valid caseID starts at 1
        await ctx.respond("You have to enter a caseID (a number, issued with your case. Maybe check the /triallist if you forgot)")
    else:
        role = discord.utils.get(ctx.guild.roles, name="Judge")
        if role in ctx.author.roles:
            if (not caseid.isnumeric()):
                await ctx.respond("invalid case ID")
            else:
                caseindex = await caseUpdateCheck(caseid)
                if (caseindex == -1): 
                    await ctx.respond("No such Case ID on record. Remember that completed cases and accusations without at least 2 witnesses are deleted from the record after a fixed time period. See "+prefix+"help");
                else:
                    if (caselist[caseindex].completetrial or (not caselist[caseindex].activetrial)):
                        await ctx.respond("("+caseid+")You can only rule on cases which are actively in trial.")
                    else:
                        if (caselist[caseindex].judge == str(ctx.author)):
                            targetUser = ctx.guild.get_member_named(str(caselist[caseindex].defendant))
                            if targetUser:
                              outputstring = "({})The judge has decided. {} is: ".format(caseid, targetUser.mention)
                            else:
                              outputstring = "({})The judge has decided. {} is: ".format(caseid, caselist[caseindex].defendant)
                            outputstring += verdict
                            if ((verdict.lower() == "innocent") or (verdict.lower() == "not guilty")):
                              outputstring += "\n The tribunal recommends issuing penalty 0, `Acquit`, to close the case."
                            caselist[caseindex].record.append((9, outputstring))
                            await ctx.respond(outputstring)
                        else:
                            await ctx.respond("Only the presiding judge may rule in this case")
        else:
            await ctx.respond("You do not have the required role to perform this command.")
    await serializeCaseList()

  
# - Consult
#____________ consult _______________
@bot.slash_command(guild_ids = guild_ids, description = "JUDGE ONLY: Give advice to the acting judge, or request advice from another judge.")
async def consult(ctx, caseid: discord.Option(str, "Numeric ID from TrialList.", required = True), consultation: discord.Option(str, "Advice or request for advice.", required = True)):
    #await deserializeCaseList()
    if (caseid == "0"): #valid caseID starts at 1
        await ctx.respond("You have to enter a caseID (a number, issued with your case. Maybe check the /triallist if you forgot)")
    else:
        role = discord.utils.get(ctx.guild.roles, name="Judge")
        if role in ctx.author.roles:
            if (not caseid.isnumeric()):
                await ctx.respond("invalid case ID")
            else:
                caseindex = await caseUpdateCheck(caseid)
                if (caseindex == -1): 
                    await ctx.respond("No such Case ID on record. Remember that completed cases and accusations without at least 2 witnesses are deleted from the record after a fixed time period.");
                else:
                    if (caselist[caseindex].completetrial or (not caselist[caseindex].activetrial)):
                        await ctx.respond("("+caseid+")You can only rule on cases which are actively in trial.")
                    else:
                        if (caselist[caseindex].judge == str(ctx.author)):
                            outputstring = "("+caseid+")The presiding judge requests consultation with note: "
                            outputstring += consultation
                            caselist[caseindex].record.append((8, outputstring))
                            await ctx.respond(outputstring)
                        else:
                            outputstring = "({})The Honorable Judge {} offers the following consultation: ".format(caseid, str(ctx.author))
                            outputstring += consultation
                            caselist[caseindex].record.append((8, outputstring))
                            await ctx.respond(outputstring)
        else:
            await ctx.respond("You do not have the required role to perform this command.")
    await serializeCaseList()

# - Penalize
#____________ penalize _______________

async def get_penalty_list(ctx: discord.AutocompleteContext):
  return penaltyList

#penaltyList = ["Acquit", "Nick-Change", "Chastize", "Luther Chastize", "Minute Mute", "Hour Mute", "Kick", "Day Ban", "Permaban"]

@bot.slash_command(guild_ids = guild_ids, description = "JUDGE ONLY: Issue penalty for a case.")
async def penalize(ctx, caseid: discord.Option(str, "Numeric ID from TrialList.", required=True), penalty: discord.Option(str, "How to penalize.",autocomplete = get_penalty_list, required=True), deferral: discord.Option(str, "1 (default) if the accuser should execute, 0 to execute immediately.", default="1", required=False), modifier: discord.Option(str, "Special options (e.g. silly name).", default = "", required=False)):
    #await deserializeCaseList()
    if (caseid == "0"): #valid caseID starts at 1
        await ctx.respond("You have to enter a caseID (a number, issued with your case. Maybe check the /triallist if you forgot)")
    else:
        if (penalty not in penaltyList):
            await ctx.respond("You have to enter a valid penaltyID (Check /penalties for the list)")
        else:
            role = discord.utils.get(ctx.guild.roles, name="Judge")
            if role in ctx.author.roles:
                if (((not str(caseid).isnumeric()) or (not str(deferral).isnumeric())) or
                    (int(deferral) < 0) or (int(deferral) > 1)):
                    await ctx.respond("The case ID and deferral must be numeric values. See /penalties for appropriate penalty keys. Deferral is 1 or 0 (default 1 except for acquit), where 1 defers the right to penalize to the accuser.")
                else:
                    caseindex = await caseUpdateCheck(caseid)
                    if (caseindex == -1): 
                        await ctx.respond("No such Case ID on record. Remember that completed cases and accusations without at least 2 witnesses are deleted from the record after a fixed time period.");
                    else:
                        if (caselist[caseindex].completetrial or (not caselist[caseindex].activetrial)):
                            await ctx.respond("("+caseid+")You can only penalize for cases which are actiely in trial")
                        else:
                            if (caselist[caseindex].judge == str(ctx.author)):
                                outputstring = "("+caseid+")The judge has decided. The penalty is: "
                                caselist[caseindex].penaltyid = penalty
                                outputstring += penalty
                                if ((int(deferral) == 1) and (penalty != "Acquit")):
                                    outputstring += "\nThe responsibility to execute penalty has been delegated to the accuser."
                                    caselist[caseindex].deferredpenalty = True
                                    await ctx.respond(outputstring)
                                else:
                                    outputstring += "\nThe penalty will be carried out immediately. The case is closed."
                                    await ctx.respond(outputstring)
                                    caselist[caseindex].completetrial = True
                                    caselist[caseindex].activetrial = False
                                    caselist[caseindex].completetrial = True
                                    caselist[caseindex].trialendtime = datetime.now()
                                    #await doPenalty(caselist[caseindex].defendant, int(caselist[caseindex].penaltyid), ctx)
                                    await doPenalty(ctx, caselist[caseindex].defendant, penalty, modifier)
                                caselist[caseindex].record.append((10, outputstring))
                            else:
                                await ctx.respond("("+caseid+")Only the presiding judge may issue a penalty in this case")
            else:
                await ctx.respond("You do not have the required role to perform this command.")
    await serializeCaseList()

# - Penalties
#____________ penalties _______________
@bot.slash_command(guild_ids = guild_ids, description = "Show available penalties.")
async def penalties(ctx):
  outstring = ""
  for key, cmd, helptext in judicialpenalties:
    outstring += str(key) + "\t-\t" + cmd + "\t-\t" + helptext + "\n"
  await ctx.respond(outstring)
        
#-----------------------------------

#-----------------------------------

#callback for the dictionary autocomplete
async def get_dictionary_terms(ctx: discord.AutocompleteContext):
  return [term for term in termList if term.startswith(ctx.value.lower())]


#-----------------------------------
#--------------Dictionary Commands
#-----------------------------------
#say hello
@bot.slash_command(guild_ids = guild_ids, description = "Say hello!")
async def hello(ctx, name:str = None):
  #if name: 
  #  name = ctx.guild.get_member_named(name)
  name = name or ctx.author.mention
  await ctx.respond(f"Howdy {name}!")

#"Repeat after me"
@bot.slash_command(guild_ids = guild_ids, description = "Make the bot say something")
async def repeat(ctx, content: discord.Option(str, "Output", required = True)):
  await ctx.respond(f"{content}")

#show a definition from the dictionary db
@bot.slash_command(guild_ids = guild_ids, description = "Get the definition for a role.")
async def define(ctx, term: discord.Option(str, "the word to define",autocomplete = get_dictionary_terms, required = True)):
  key = "def " + term.lower()
  try:
    keyval = db[key]
    if (keyval != None):
      outstring = "__**Role Definition:**__ **"+string.capwords(term) + "**\n\n> " + str(keyval)
      await ctx.respond(outstring)
    else:
      await ctx.respond("Not found.")
  except KeyError:
    await ctx.respond(term+": No definition for that term. Check your spelling, and remember that we've only supplied definitions for the roles in #roles.")

#add a term to the dictionary db
@bot.slash_command(guild_ids = guild_ids, description = "ADMIN ONLY: Add a term to the dictionary.")
async def adddefinition(ctx, term: discord.Option(str, "the word to define"), definition: discord.Option(str, "the definition to add")):
    if ctx.author.guild_permissions.administrator:

        if ((len(definition) > 0) and (len(term) > 0)):
          key = "def " + term.lower().strip()
          print(definition)#.replace("\"",""))
          db[key] = definition.replace("\n", "\n> ").replace("///", "\n> \n> ").strip()
          termList.append(term)
          await ctx.respond(f"Added {term}.")
    else:
        await ctx.respond("You do not have the required role to perform this command.")

#delete a term from the dictionary db
@bot.slash_command(guild_ids = guild_ids, description = "ADMIN ONLY: Delete a term from the dictionary.")
async def deletedefinition(ctx, term: discord.Option(str, "term to delete",autocomplete = get_dictionary_terms, required = True)): 
    if ctx.author.guild_permissions.administrator:
      key = "def " + term.lower()
      keyval = db[key]
      if (keyval != None):
        del db[key]
        termList.remove(term)
        await ctx.send("deleted " + term)
      else:
        await ctx.send("Not found.")
    else:
        await ctx.send("You do not have the required role to perform this command.")


#-----------------------------------
#--------------General Bot Event Stuff
#-----------------------------------
@bot.event
async def on_ready():
  print(f"We have logged in as {bot.user}")
  #pull all the definitions from the database to compile the autocomplete list
  keys = db.prefix("def")
  for key in keys:
    termList.append(key[4:])
  #print("found keys: ")
  for term in termList:
    print(term)
  #print(bot.guilds)
  print("... added all the dictionary keys. Populating Case List.")
  await deserializeCaseList()
  await caseListCleanup()
  print("Done with Case List. Running Bot...")
  

#failure detection added
fail = 1
watchdog = 0
while (fail) and (watchdog < 5):
  try:
      bot.run(token)
      fail = 0
  except Exception as inst:
      os.system("kill 1")
      print(type(inst))    # the exception instance
      print(inst.args)     # arguments stored in .args
      print(inst)
      print("bot failed to run. Trying again in 5...")
      time.sleep(5)
      watchdog += 1
      print(watchdog)
