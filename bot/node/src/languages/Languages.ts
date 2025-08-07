interface Language {
  flag: string;
  value: string;
  localizedName: string;
  englishName: string;
  translations: Translations;
}
interface Translations {
  languageSelectString: string;
  createAProposalString: string;
  embed: EmbedData;
  patchExample: string;
}
interface EmbedData {
  title: string;
  description: string;
}
export const Languages: Language[] = [
  {
    flag: "🇬🇧",
    value: "english",
    localizedName: "English",
    englishName: "English",
    translations: {
      languageSelectString: "Select a language to propose changes to",
      createAProposalString: "Create a proposal",
      embed: {
        title: "Contributing to Vivi dictionaries",
        description: `We're welcoming contributions from the community to improve Vivi! If you have new words to add to one of our dictionaries, or have any corrections you'd like to make, you can start a proposal by pressing the button below.
### Warning
<:Warning:1333998634752151674> **Your proposal must follow the \`.patch\` file format below.**
### Creating a proposal
Proposals are centered around \`.patch\` files. View the example file below to see how to structure your proposal.
### Example`,
      },
      patchExample: `# Use comments to explain your changes.
# Or use comments to create sections.

+ ADD A WORD LIKE THIS
+ ADD ANOTHER WORD
+ USE CAPITAL LETTERS
- REMOVE WORDS LIKE THIS
- REMOVE ANOTHER
- AND ANOTHER!

# You can make comments anywhere

- AND MAKE REMOVALS
+ AND ADDITIONS
- IN ANY ORDER`,
    },
  },
  {
    flag: "🇷🇺",
    value: "russian",
    localizedName: "Русский",
    englishName: "Russian",
    translations: {
      languageSelectString: "Выберите язык для предложения изменений",
      createAProposalString: "Создать предложение",
      embed: {
        title: "Вклад в словари Вика",
        description: `Мы приветствуем вклад сообщества в улучшение Вика! Если у вас есть новые слова для добавления в один из наших словарей или какие-либо исправления, которые вы хотели бы внести, вы можете начать предложение, нажав кнопку ниже.
### Предупреждение
<:Warning:1333998634752151674> **Ваше предложение должно следовать формату файла \`.patch\` ниже.**
### Создание предложения
Предложения строятся вокруг файлов \`.patch\`. Посмотрите пример файла ниже, чтобы увидеть, как структурировать ваше предложение.
### Пример`,
      },
      patchExample: `# Используйте комментарии, чтобы объяснить ваши изменения.
# Или используйте комментарии для создания разделов.

+ добавьте слово вот так
+ добавьте ещё одно слово
- удаляйте слова вот так
- удалите ещё одно
- и ещё одно!

# Вы можете делать комментарии где угодно

- и делать удаления
+ и добавления
- в любом порядке`,
    },
  },
];

export function getLanguage(value: string): Language | undefined {
  const [result] = Languages.filter((language) => language.value === value);
  return result;
}
