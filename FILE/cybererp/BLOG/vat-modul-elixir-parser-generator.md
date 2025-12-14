# VAT Модул в Elixir: Parser, Generator и Deklar за НАП декларации

## Въведение

След успешната имплементация на [VAT модул в Rust](https://github.com/yourusername/vat-rust), представяме и Elixir версията, интегрирана в **Cyber ERP** системата. Този модул автоматизира генерирането и парсирането на ДДС декларации в текстовия формат, изискван от НАП (Национална агенция по приходите).

## Защо Elixir за VAT обработка?

### Предимства на Elixir за финансови системи

1. **Immutability (Неизменност)** - веднъж създадените данни не могат да бъдат променени, което осигурява:
   - Пълна одит следа
   - Невъзможност за случайно корумпиране на данни
   - Thread-safety по дефиниция

2. **Decimal точност** - за разлика от JavaScript или други езици, Elixir има вградена библиотека `Decimal` за финансови изчисления:
   ```elixir
   # Няма грешки при закръгляване
   Decimal.add("0.1", "0.2") == Decimal.new("0.3")  # true
   # Докато в JavaScript: 0.1 + 0.2 === 0.3  // false
   ```

3. **Fault tolerance (Толерантност към грешки)** - Erlang VM (BEAM) осигурява:
   - Автоматично възстановяване при crash
   - Изолация на грешки
   - 99.9999999% uptime в телеком системи

4. **Конкурентност** - лесно обработка на хиляди клиенти едновременно
   - Lightweight процеси (не OS threads)
   - Millisecond scheduling
   - Автоматичен garbage collection на процес ниво

## Архитектура на VAT модула

Модулът е разделен на три основни компонента:

```
CyberCore.Vat
├── Parser    - Парсиране на TXT файлове от НАП
├── Generator - Генериране на PRODAGBI.TXT и POKUPKI.TXT
└── Deklar    - Генериране на обобщителния DEKLAR.TXT
```

### 1. Parser - Парсиране на декларации

Parser модулът чете фиксирани текстови формати според спецификацията на НАП.

#### Формат на PRODAGBI.TXT (Продажби)

Всеки ред представлява една фактура за продажба с фиксирана дължина на полетата:

| Поле | Позиция | Дължина | Тип | Описание |
|------|---------|---------|-----|----------|
| 02-00 | 0-15 | 15 | String | ЕИК на фирмата |
| 02-01 | 15-21 | 6 | String | Период (YYYYMM) |
| 02-02 | 21-25 | 4 | String | Корекционен номер |
| 02-03 | 25-40 | 15 | String | Пореден номер |
| 02-04 | 40-42 | 2 | String | Тип документ |
| 02-05 | 42-62 | 20 | String | Номер на документ |
| 02-06 | 62-72 | 10 | String | Дата (DD/MM/YYYY) |
| 02-07 | 72-87 | 15 | String | ДДС номер на получател |
| 02-08 | 87-137 | 50 | String | Име на получател |
| 02-09 | 137-167 | 30 | String | Предмет на доставка |
| 02-10 | 167-182 | 15 | Decimal | Данъчна основа (20%) |
| 02-11 | 182-197 | 15 | Decimal | ДДС сума (20%) |
| ... | ... | ... | ... | ... |

#### Имплементация на Parser

```elixir
defmodule CyberCore.Vat.Parser do
  @moduledoc """
  Парсиране на VAT декларации в текстов формат според НАП спецификация.
  """

  @prodagbi_schema [
    {"02-00", 0, 15, :string},    # ЕИК
    {"02-01", 15, 6, :string},     # Период
    {"02-02", 21, 4, :string},     # Корекция
    {"02-03", 25, 15, :string},    # Пореден номер
    {"02-04", 40, 2, :string},     # Тип документ
    {"02-05", 42, 20, :string},    # Номер документ
    {"02-06", 62, 10, :string},    # Дата
    {"02-07", 72, 15, :string},    # ДДС номер получател
    {"02-08", 87, 50, :string},    # Име получател
    {"02-09", 137, 30, :string},   # Предмет
    {"02-10", 167, 15, :decimal},  # Данъчна основа 20%
    {"02-11", 182, 15, :decimal},  # ДДС 20%
    {"02-12", 197, 15, :decimal},  # Данъчна основа 9%
    # ... останалите полета
  ]

  def parse_prodagbi(content) do
    content
    |> String.split("\r\n", trim: true)
    |> Enum.map(&parse_prodagbi_line/1)
  end

  defp parse_prodagbi_line(line) do
    @prodagbi_schema
    |> Enum.reduce(%{}, fn {key, start, len, type}, acc ->
      value = extract_value(line, start, len, type)
      Map.put(acc, key, value)
    end)
  end

  defp extract_value(line, start, length, :decimal) do
    line
    |> String.slice(start, length)
    |> String.trim()
    |> case do
      "" -> Decimal.new(0)
      val -> Decimal.new(val)
    end
  end

  defp extract_value(line, start, length, :string) do
    line
    |> String.slice(start, length)
    |> String.trim()
  end
end
```

#### Пример за парсиране

```elixir
# Четене на файл
{:ok, content} = File.read("PRODAGBI.TXT")

# Парсиране
invoices = CyberCore.Vat.Parser.parse_prodagbi(content)

# Резултат - списък от maps
[
  %{
    "02-00" => "BG202210896",
    "02-01" => "202506",
    "02-05" => "0000001045",
    "02-06" => "02/06/2025",
    "02-07" => "000124051",
    "02-08" => "Министерство на здравеопазването",
    "02-10" => Decimal.new("196.00"),
    "02-11" => Decimal.new("39.20"),
    # ...
  },
  # ...
]
```

### 2. Generator - Генериране на декларации

Generator модулът автоматично извлича данни от базата и генерира файловете в правилния формат.

#### Имплементация

```elixir
defmodule CyberCore.Vat.Generator do
  @moduledoc """
  Генериране на VAT декларации от системни данни.
  """

  alias CyberCore.Repo
  alias CyberCore.Sales.Invoice
  import Ecto.Query

  def generate_prodagbi_txt(tenant_id, year, month) do
    # Извличане на фактури за периода
    start_date = Date.new!(year, month, 1)
    end_date = Date.end_of_month(start_date)

    invoices =
      from(i in Invoice,
        where: i.tenant_id == ^tenant_id and
               i.issue_date >= ^start_date and
               i.issue_date <= ^end_date,
        preload: [:contact]
      )
      |> Repo.all()

    # Форматиране на всяка фактура като ред
    invoices
    |> Enum.with_index(1)
    |> Enum.map_join("\r\n", fn {invoice, index} ->
      format_prodagbi_line(invoice, index)
    end)
  end

  defp format_prodagbi_line(invoice, index) do
    [
      format_field(invoice.tenant_id, 15),
      format_field(format_period(invoice.issue_date), 6),
      format_field(0, 4, :numeric),
      format_field(index, 15, :numeric),
      format_field(invoice.vat_document_type || "01", 2),
      format_field(invoice.invoice_no, 20),
      format_field(format_date(invoice.issue_date), 10),
      format_field(invoice.contact.vat_number, 15),
      format_field(invoice.contact.name, 50),
      format_field("Предмет на доставката", 30),
      format_field(invoice.subtotal, 15, :numeric),
      format_field(invoice.tax_amount, 15, :numeric),
      # Останалите полета с 0
      format_field(0, 15, :numeric),
      # ...
    ]
    |> Enum.join("")
  end

  # Форматиране на поле с правилна дължина и padding
  defp format_field(value, length, type \\ :symbolic) do
    string_value =
      case {type, value} do
        {:numeric, num} when is_integer(num) ->
          Decimal.new(num) |> Decimal.to_string(:normal)
        {:numeric, %Decimal{} = dec} ->
          Decimal.to_string(dec, :normal)
        {_, val} ->
          to_string(val)
      end

    # Текстови полета - padding отдясно
    # Числови полета - padding отляво
    cond do
      String.length(string_value) > length ->
        String.slice(string_value, 0, length)
      type == :numeric ->
        String.pad_leading(string_value, length, " ")
      true ->
        String.pad_trailing(string_value, length, " ")
    end
  end

  defp format_date(date) do
    Calendar.strftime(date, "%d/%m/%Y")
  end

  defp format_period(date) do
    Calendar.strftime(date, "%Y%m")
  end
end
```

#### Използване

```elixir
# Генериране на PRODAGBI.TXT за юни 2025
prodagbi_content = CyberCore.Vat.Generator.generate_prodagbi_txt(1, 2025, 6)
File.write!("PRODAGBI.TXT", prodagbi_content)

# Генериране на POKUPKI.TXT
pokupki_content = CyberCore.Vat.Generator.generate_pokupki_txt(1, 2025, 6)
File.write!("POKUPKI.TXT", pokupki_content)
```

### 3. Deklar - Обобщителна декларация

Deklar модулът генерира обобщителния файл DEKLAR.TXT, който съдържа сумарни данни.

#### Структура на DEKLAR.TXT

```
┌─────────────────┬──────────────────────────────────┐
│ Поле            │ Описание                         │
├─────────────────┼──────────────────────────────────┤
│ ЕИК             │ BG202210896                      │
│ Име на фирма    │ Демо ЕООД                        │
│ Период          │ 202506                           │
│ Брой продажби   │ 23                               │
│ Брой покупки    │ 58                               │
│ Клетка 01       │ Сума данъчна основа 20%          │
│ Клетка 11       │ Сума ДДС 20%                     │
│ Клетка 30       │ Сума покупки данъчна основа      │
│ Клетка 41       │ Сума покупки ДДС                 │
│ ...             │ ...                              │
└─────────────────┴──────────────────────────────────┘
```

#### Имплементация

```elixir
defmodule CyberCore.Vat.Deklar do
  @moduledoc """
  Генериране на DEKLAR.TXT - обобщителна декларация.
  """

  def generate_deklar_txt(tenant_id, year, month, prodagbi_content, pokupki_content) do
    # Парсиране на генерираните файлове
    prodagbi_data = CyberCore.Vat.Parser.parse_prodagbi(prodagbi_content)
    pokupki_data = CyberCore.Vat.Parser.parse_pokupki(pokupki_content)

    # Изчисляване на клетки от декларацията
    kletka_01 = sum_field(prodagbi_data, "02-10")  # Данъчна основа 20%
    kletka_11 = sum_field(prodagbi_data, "02-11")  # ДДС 20%
    kletka_30 = sum_field(pokupki_data, "03-10")   # Покупки данъчна основа
    kletka_41 = sum_field(pokupki_data, "03-13")   # Покупки ДДС

    # Форматиране на файла
    [
      format_field(tenant_id, 15),
      format_field("Демо ЕООД", 50),
      format_field(format_period(year, month), 6),
      format_field("Име на подаващия", 50),
      format_field(length(prodagbi_data), 15, :numeric),
      format_field(length(pokupki_data), 15, :numeric),
      format_field(kletka_01, 15, :numeric),
      format_field(kletka_11, 15, :numeric),
      format_field(kletka_30, 15, :numeric),
      format_field(kletka_41, 15, :numeric),
      # ... всички останали клетки
    ]
    |> Enum.join("")
  end

  defp sum_field(data, field_key) do
    data
    |> Enum.map(&Map.get(&1, field_key, Decimal.new(0)))
    |> Enum.reduce(Decimal.new(0), &Decimal.add/2)
  end

  defp format_period(year, month) do
    year_str = to_string(year)
    month_str = String.pad_leading(to_string(month), 2, "0")
    "#{year_str}#{month_str}"
  end
end
```

## Пълен работен пример

```elixir
# 1. Генериране на файлове за месец юни 2025
tenant_id = 1
year = 2025
month = 6

# 2. Генериране на PRODAGBI.TXT
prodagbi = CyberCore.Vat.Generator.generate_prodagbi_txt(tenant_id, year, month)
File.write!("PRODAGBI.TXT", prodagbi)

# 3. Генериране на POKUPKI.TXT
pokupki = CyberCore.Vat.Generator.generate_pokupki_txt(tenant_id, year, month)
File.write!("POKUPKI.TXT", pokupki)

# 4. Генериране на DEKLAR.TXT
deklar = CyberCore.Vat.Deklar.generate_deklar_txt(
  tenant_id,
  year,
  month,
  prodagbi,
  pokupki
)
File.write!("DEKLAR.TXT", deklar)

# 5. Парсиране и валидация
parsed_prodagbi = CyberCore.Vat.Parser.parse_prodagbi(prodagbi)
IO.puts("Брой продажби: #{length(parsed_prodagbi)}")

# 6. Проверка на суми
total_vat =
  parsed_prodagbi
  |> Enum.map(&Map.get(&1, "02-11"))
  |> Enum.reduce(Decimal.new(0), &Decimal.add/2)

IO.puts("Общо ДДС за внасяне: #{Decimal.to_string(total_vat, :normal)} лв")
```

## Mix Task за CLI употреба

```elixir
defmodule Mix.Tasks.Vat.Generate do
  use Mix.Task

  @shortdoc "Генериране на VAT файлове за НАП"

  def run([tenant_id, year, month]) do
    Mix.Task.run("app.start")

    tenant_id = String.to_integer(tenant_id)
    year = String.to_integer(year)
    month = String.to_integer(month)

    IO.puts("Генериране на VAT файлове...")
    IO.puts("Tenant: #{tenant_id}, Период: #{year}-#{month}")

    # Генериране
    prodagbi = CyberCore.Vat.Generator.generate_prodagbi_txt(tenant_id, year, month)
    pokupki = CyberCore.Vat.Generator.generate_pokupki_txt(tenant_id, year, month)
    deklar = CyberCore.Vat.Deklar.generate_deklar_txt(tenant_id, year, month, prodagbi, pokupki)

    # Запис
    output_dir = "vat_export_#{year}_#{String.pad_leading(to_string(month), 2, "0")}"
    File.mkdir_p!(output_dir)

    File.write!("#{output_dir}/PRODAGBI.TXT", prodagbi)
    File.write!("#{output_dir}/POKUPKI.TXT", pokupki)
    File.write!("#{output_dir}/DEKLAR.TXT", deklar)

    IO.puts("✓ Файловете са записани в #{output_dir}/")
  end
end
```

Използване:
```bash
mix vat.generate 1 2025 6
```

## Тестване

```elixir
defmodule CyberCore.VatTest do
  use CyberCore.DataCase

  alias CyberCore.Vat.{Parser, Generator, Deklar}

  describe "Parser" do
    test "парсира PRODAGBI.TXT файл" do
      content = """
      BG202210896    202506   0              1010000001045          02/06/2025000124051      Клиент 1                                          Стоки                                  196.00          39.20         196.00          39.20           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00
      """

      result = Parser.parse_prodagbi(content)

      assert length(result) == 1
      assert hd(result)["02-00"] == "BG202210896"
      assert Decimal.equal?(hd(result)["02-10"], Decimal.new("196.00"))
      assert Decimal.equal?(hd(result)["02-11"], Decimal.new("39.20"))
    end
  end

  describe "Generator" do
    test "генерира PRODAGBI.TXT от фактури" do
      # Setup - създаване на тестови фактури
      tenant = insert(:tenant, vat_number: "BG202210896")
      contact = insert(:contact, tenant: tenant, vat_number: "BG123456789")

      invoice = insert(:invoice,
        tenant: tenant,
        contact: contact,
        issue_date: ~D[2025-06-02],
        subtotal: Decimal.new("100.00"),
        tax_amount: Decimal.new("20.00")
      )

      # Генериране
      result = Generator.generate_prodagbi_txt(tenant.id, 2025, 6)

      # Валидация
      assert String.contains?(result, "BG202210896")
      assert String.contains?(result, "202506")
      assert String.contains?(result, "BG123456789")
    end
  end

  describe "Deklar" do
    test "изчислява правилно клетки" do
      prodagbi = """
      BG202210896    202506   0              1010000001045          02/06/2025000124051      Клиент                                            Стоки                                  196.00          39.20           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00
      BG202210896    202506   0              2010000001046          03/06/2025000124052      Клиент 2                                          Услуги                                 100.00          20.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00           0.00
      """

      pokupki = ""

      result = Deklar.generate_deklar_txt(1, 2025, 6, prodagbi, pokupki)

      # Проверка че декларацията съдържа правилни суми
      assert String.contains?(result, "296.00")  # 196 + 100
      assert String.contains?(result, "59.20")   # 39.20 + 20
    end
  end
end
```

## Сравнение с Rust имплементацията

| Аспект | Elixir | Rust |
|--------|--------|------|
| **Performance** | ~10-50ms за 1000 фактури | ~1-5ms за 1000 фактури |
| **Memory** | По-висока (GC overhead) | По-ниска (zero-cost abstractions) |
| **Concurrency** | Отлична (actor model) | Отлична (async/await) |
| **Decimal точност** | Вградена (`Decimal`) | External crate (`rust_decimal`) |
| **Error handling** | Pattern matching, {:ok/:error} | Result<T, E>, Option<T> |
| **Hot code reload** | ✅ Да (в production!) | ❌ Не |
| **Learning curve** | Средна | Висока (ownership, lifetimes) |
| **Ecosystem** | Phoenix, Ecto, LiveView | Actix, Diesel, Yew |

## Интеграция в Cyber ERP

В реалната система модулът е интегриран в Phoenix LiveView интерфейс:

```elixir
defmodule CyberWeb.VatLive.Export do
  use CyberWeb, :live_view

  def mount(_params, _session, socket) do
    {:ok, assign(socket, year: 2025, month: 6)}
  end

  def handle_event("generate", %{"year" => year, "month" => month}, socket) do
    tenant_id = socket.assigns.current_tenant.id
    year = String.to_integer(year)
    month = String.to_integer(month)

    # Асинхронно генериране
    Task.async(fn ->
      CyberCore.Vat.Generator.generate_prodagbi_txt(tenant_id, year, month)
    end)

    {:noreply, socket}
  end

  def handle_info({_ref, result}, socket) do
    # Изпращане на файла за download
    {:noreply, push_download(socket, result, "PRODAGBI.TXT")}
  end
end
```

## Заключение

Elixir VAT модулът демонстрира как съвременен функционален език може елегантно да реши сложен бизнес проблем:

- ✅ **Тип безопасност** с pattern matching
- ✅ **Decimal точност** за финансови изчисления
- ✅ **Immutability** за одит и reproducibility
- ✅ **Fault tolerance** с Erlang VM
- ✅ **Hot code reload** за zero-downtime updates
- ✅ **Конкурентност** за processing на хиляди декларации

Комбинацията от **Parser**, **Generator** и **Deklar** модули осигурява пълна автоматизация на VAT процеса - от въвеждане на фактури до генериране на готови файлове за НАП.

---

## Ресурси

- [Cyber ERP GitHub](https://github.com/yourusername/cyber-erp)
- [Elixir Decimal Library](https://hexdocs.pm/decimal)
- [Phoenix Framework](https://phoenixframework.org)
- [НАП Формат спецификация](https://nap.bg)

---

**Технически детайли:**
- **Език:** Elixir 1.16+
- **Dependencies:** Decimal, Ecto, Phoenix
- **Тестване:** ExUnit
- **CI/CD:** GitHub Actions
- **Лиценз:** MIT

---

*Статията е част от техническата документация на **Cyber ERP** - модерна ERP система за счетоводство.*
