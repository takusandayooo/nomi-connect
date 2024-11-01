import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from middleware import ApiKeys


class Group(BaseModel):
    group_name: str
    overview: str
    usernames: list[str]


class _GroupList(BaseModel):
    groups: list[Group]


class Introduction(BaseModel):
    username: str
    content: str


class _IntroductionList(BaseModel):
    introductions: list[Introduction]


def split_groups_by(
    api_keys: ApiKeys, intros: list[Introduction]
) -> list[Group] | None:
    if len(intros) == 0:
        return None

    intro_json: str = _IntroductionList(introductions=intros).model_dump_json()

    client = OpenAI(api_key=api_keys.openai_api_key)
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        response_format=_GroupList,
        messages=[
            {
                "role": "system",
                "content": """
# 役割

あなたはチームビルディングが得意なマネージャーです。

# やること

自己紹介を元に、似ている人をグループ分けしてください。ただし、注意点を守ってください。

# 与えられるデータ構造

複数の人の自己紹介がリストとして与えられます。自己紹介のデータ構造は以下の通りです。

## 自己紹介のデータ構造

それぞれの人の自己紹介は以下のデータ構造で与えられます。

```json
{
  "username": <名前>,
  "content": <自己紹介の内容>
}
```

# 注意点

- 自己紹介文が少しでも似ていたら同じグループにする
- その他、適切なグループ分けを行う
    """,
            },
            {
                "role": "user",
                "content": intro_json,
            },
        ],
    )

    group_list: _GroupList | None = response.choices[0].message.parsed
    if group_list is None:
        return None
    return group_list.groups


if __name__ == "__main__":
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    assert openai_api_key is not None
    search_api_key = os.getenv("SEARCH_API_KEY")
    assert search_api_key is not None
    api_keys = ApiKeys(openai_api_key=openai_api_key, search_api_key=search_api_key)

    data = [
        Introduction(
            username="達郎", content="スポーツが好きでボクシングをやってます。"
        ),
        Introduction(
            username="美咲",
            content="最近、料理にハマっています。特に和食を作るのが好きです。",
        ),
        Introduction(
            username="健太",
            content="アウトドアが大好きで、週末はよくハイキングに行きます。",
        ),
        Introduction(
            username="真理子", content="読書が趣味で、特にファンタジー小説が好きです。"
        ),
        Introduction(
            username="翔太", content="映画鑑賞が趣味で、特にアクション映画が好きです。"
        ),
    ]
    print(split_groups_by(api_keys, data))
