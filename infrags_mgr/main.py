from memory_store import MemoryStore
from infrags_mgr.openai_chatbot import Chatbot
from datetime import datetime

def main():
    store = MemoryStore()
    bot = Chatbot()

    print("\n🧠 Bienvenue dans ton assistant mémoire !")
    while True:
        print("\nQue veux-tu faire ?")
        print("1. Ajouter un souvenir (texte)")
        print("2. Ajouter un souvenir (voix)")
        print("3. Poser une question")
        print("4. Quitter")

        choice = input("Choix : ").strip()
        if choice == "1":
            text = input("Entre ton souvenir :\n> ")
            date = input("Date (laisse vide pour aujourd'hui) : ").strip()
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            store.add_memory(text, date)
            print("✅ Souvenir enregistré.")

        elif choice == "2":
            from voice_input import record_voice
            text = record_voice()
            if text:
                date = datetime.now().strftime("%Y-%m-%d")
                store.add_memory(text, date)
                print("✅ Souvenir vocal enregistré.")

        elif choice == "3":
            question = input("Quelle est ta question ?\n> ")
            memories = store.search_memories(question)
            print("\n📚 Souvenirs pertinents trouvés :")
            for m in memories:
                print(f"- {m['text']} ({m['date']})")
            print("\n🤖 Réponse du chatbot :")
            print(bot.ask(question, memories))

        elif choice == "4":
            print("À bientôt ! 🖐️")
            break

        else:
            print("Choix non reconnu.")

if __name__ == "__main__":
    main()
