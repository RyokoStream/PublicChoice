{% extends "global/Page.html" %}

{% block title %}
    {% if is_ambiguity %}選択課題(確率不明){% else %}選択課題{% endif %}
{% endblock %}

{% block content %}

    <style>
        .instructions {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 6px solid #007bff;
            margin-bottom: 30px;
        }
        .table-mpl td {
            padding: 15px !important;
            vertical-align: middle;
        }
        .text-center { text-align: center; }
        .text-end { text-align: right; }
        input[type="radio"] { 
            transform: scale(1.4); 
            cursor: pointer; 
        }
    </style>

    <div class="instructions">
        <p>以下の各行について、どちらか好きな方を選んでください。</p>
        <p>現在のオプション：<b>{{ lottery_text }}</b></p>
    </div>

    <table class="table table-hover table-mpl">
        <thead>
            <tr>
                <th>No.</th>
                <th class="text-center">選択A (確実)</th>
                <th class="text-center">A</th>
                <th class="text-center">B</th>
                <th class="text-center">選択B (くじ)</th>
            </tr>
        </thead>
        <tbody>
            {% for row in rows %}
            <tr>
                <td class="text-muted">{{ forloop.counter }}</td>
                <td class="text-end">
                    <b>{{ row.label }}</b> を確実にもらう
                </td>
                <td class="text-center">
                    <input type="radio" name="{{ row.field_name }}" value="2" required>
                </td>
                <td class="text-center">
                    <input type="radio" name="{{ row.field_name }}" value="1" required>
                </td>
                <td>
                    {{ lottery_text }}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <div cla
