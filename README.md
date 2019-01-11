# Programming vacancies compare

Using this console-script, you can get statistics data for programmers salary in `Moscow city`.
Statistics represented by data-tables grouped by programming languages.
Script gets data from the following sites-api:
- [hh.ru](https://api.hh.ru)
- [superjob.ru](https://api.superjob.ru) 

![alt-текст](https://github.com/nicko858/vacancies_compare/blob/master/%D0%92%D1%8B%D0%B4%D0%B5%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5_019.png)

### How to install
Python3 should be already installed.
```bash
$ git clone https://github.com/nicko858/vacancies_compare.git
$ cd fiasko_bro
$ pip install -r requirements.txt
```

- Create account on the [superjob.ru](https://api.superjob.ru), or use existing
- Register new application following this [link](https://api.superjob.ru/register)
- Remember your secret key
- Create file `.env` in the script directory
- Add the following records to the `.env-file`:
   - secret_key = `Your secret key`
- The [hh.ru](https://api.hh.ru) doesn't requires authentification 


### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).
