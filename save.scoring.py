import pyray


class Save_Scoring:
    def __init__(self, file_path='scores.txt'):
        self.file_path = file_path

    def save_score(self, player_name, score):
        try:
            with open(self.file_path, 'a') as file:
                file.write(f'{player_name}: {score}\n')
        except Exception as e:
            print(f"Ошибка при сохранении очков: {e}")

    def load_scores(self):
        scores = []
        try:
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    player, score = line.strip().split(': ')
                    scores.append((player, int(score)))
        except FileNotFoundError:
            print("Файл с очками не найден.")
        except Exception as e:
            print(f"Ошибка при загрузке очков: {e}")
        return scores
    
    def add_score(self, player_name, player_score):
        scores = []
        with open(self.file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                player, score = line.strip().split(': ')
                scores.append({'name': player, 'score': int(score)})
        if len(scores) < 10:
            scores.append({'name': player_name, 'score': int(player_score)})
        elif scores[9]['score'] < player_score:
            scores.append({'name': player_name, 'score': int(player_score)})
            scores.pop(9)
        scores = sorted(scores, key=lambda x: x['score'], reverse=True)
        with open(self.file_path, 'r') as file:
            for item in scores:
                file.write(str(item['name'])+': ' + str(item['score']) + '\n')
            file.close()


def main():
    player_name = input("Введите ваше имя: ")

    pacman = Save_Scoring()

    # Имитация процесса игры, когда игрок зарабатывает очки
    score = 50

    # Сохранение очков
    pacman.save_score(player_name, score)

    # Загрузка и вывод списка очков
    scores = pacman.load_scores()
    if scores:
        print("Текущие очки:")
        for player, score in scores:
            print(f"{player}: {score}")


if __name__ == "__main__":
    main()
