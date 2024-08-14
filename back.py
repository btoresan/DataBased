from dataEngine import Database

db = Database("proton.db")

#Mude caso queira recriar a tabela
if True:
    db.create_table("jogos", 
                    ["AppID", "Title", "Relase-Date", "Deck-Verified", "Rating", "Chromebook-Ready", "Developer"])

    db.create_table("Index", ["Title", "AppID"])

