"""FanLang Streamlit 组件模块。

提供可直接嵌入 Streamlit 应用的交互组件：
- render_symbol_bar：符号栏（一行符号按钮）
- render_symbol_picker：展开式符号选择器（按梯队分组）
- render_terminology_tooltip：术语悬停提示卡片

符号数据从 fanlang 核心包获取（`from fanlang.symbols import get_all_symbols`），
本模块不重复定义符号数据，仅负责渲染逻辑。
"""

from __future__ import annotations

from typing import Any, Optional

import streamlit as st

from .callbacks import get_selected_symbol, on_symbol_click
from .styles import inject_styles

# ── 8 个核心符号及其 Emoji 映射 ──────────────────────────────
# 当 render_symbol_bar 使用默认参数时展示这组符号。
# 注意：符号语义定义来自 fanlang 核心包；此处仅维护渲染用 emoji 映射。
_CORE_SYMBOL_CHARS: list[str] = ["写", "改", "翻", "总", "问", "查", "比", "理"]

_CORE_SYMBOL_EMOJIS: dict[str, str] = {
    "写": "✍️",
    "改": "✏️",
    "翻": "🔄",
    "总": "📝",
    "问": "❓",
    "查": "🔍",
    "比": "⚖️",
    "理": "📋",
}

# ── 梯队标签 ──────────────────────────────────────────────────
_TIER_LABELS: dict[int, str] = {
    1: "一梯队 · 7 个核心符号",
    2: "二梯队 · 5 个扩展符号",
    3: "三梯队 · 8 个领域符号",
    4: "四梯队 · 5 个辅助符号",
}


# ═══════════════════════════════════════════════════════════════
# 内部辅助函数
# ═══════════════════════════════════════════════════════════════

def _attr(symbol: Any, key: str, default: Any = None) -> Any:
    """兼容 dict 和 object 的属性访问器。

    支持从 fanlang 核心包返回的 dict 或 dataclass 对象中提取属性。

    Args:
        symbol: 符号数据（dict 或对象）。
        key: 属性名。
        default: 属性不存在时的默认值。

    Returns:
        属性值。
    """
    if isinstance(symbol, dict):
        return symbol.get(key, default)
    return getattr(symbol, key, default)


def _emoji_for(symbol: Any) -> str:
    """获取符号对应的 emoji。

    优先从 fanlang 符号数据中读取 emoji 字段，回退到本地映射。

    Args:
        symbol: 符号数据。

    Returns:
        emoji 字符串。
    """
    char: str = _attr(symbol, "character", "")
    emoji: str = _attr(symbol, "emoji", "")
    if emoji:
        return emoji
    return _CORE_SYMBOL_EMOJIS.get(char, "")


def _resolve_symbols(
    symbols: Optional[list[Any]],
    default_chars: list[str],
) -> list[dict[str, Any]]:
    """解析符号列表：若用户提供自定义列表则直接使用，否则从 fanlang 核心包获取。

    优先通过 fanlang.symbols.get_all_symbols() 获取全量符号并筛选出
    default_chars 中指定的字符。若 fanlang 不可用，则用本地映射降级。

    Args:
        symbols: 用户传入的符号列表（可为 None）。
        default_chars: 默认符号字符列表。

    Returns:
        规范化后的符号列表，每个元素为包含 character 和 emoji 的 dict。
    """
    if symbols is not None:
        return symbols  # type: ignore[return-value]

    # 尝试从 fanlang 核心包获取符号数据
    try:
        from fanlang.symbols import get_all_symbols  # type: ignore[import-untyped]

        all_syms: list[Any] = get_all_symbols()
        # 筛选出默认核心符号
        result: list[dict[str, Any]] = []
        for sym in all_syms:
            char = _attr(sym, "character", "")
            if char in default_chars:
                result.append(sym)
        if result:
            return result
    except ImportError:
        pass

    # 降级：使用本地 emoji 映射构建
    result = []
    for char in default_chars:
        result.append({
            "character": char,
            "emoji": _CORE_SYMBOL_EMOJIS.get(char, ""),
            "tier": 1,
            "name_en": "",
            "name_zh": char,
        })
    return result


def _group_by_tier(symbols: list[Any]) -> dict[int, list[Any]]:
    """按梯队（tier）对符号列表进行分组。

    Args:
        symbols: 符号列表。

    Returns:
        梯队编号到符号子列表的映射。
    """
    groups: dict[int, list[Any]] = {1: [], 2: [], 3: [], 4: []}
    for sym in symbols:
        tier: int = _attr(sym, "tier", 1)
        groups.setdefault(tier, []).append(sym)
    return groups


def _tier_symbol_counts() -> dict[int, int]:
    """各梯队默认符号数量。用于 display 展示。

    Returns:
        梯队编号到数量的映射。
    """
    return {1: 7, 2: 5, 3: 8, 4: 5}


# ═══════════════════════════════════════════════════════════════
# 对外组件
# ═══════════════════════════════════════════════════════════════

def render_symbol_bar(
    symbols: Optional[list[Any]] = None,
    max_cols: int = 8,
) -> Optional[str]:
    """渲染一行 FanLang 符号按钮栏。

    默认展示 8 个核心符号（写、改、翻、总、问、查、比、理），
    每个按钮包含 emoji + 中文字符。
    使用 st.columns 实现栅格布局，支持自定义符号列表和最大列数。
    被点击的符号会通过 session_state 记录选中状态并应用高亮样式。

    Args:
        symbols: 自定义符号列表。传入 None 则使用默认 8 个核心符号。
                 列表中每个元素应为 dict 或对象，需包含 ``character`` 字段。
        max_cols: 最大列数，默认 8。按钮数量超过该值时自动折行。

    Returns:
        本次点击的符号字符（str），未点击任何按钮时返回 None。

    Example:
        >>> selected = render_symbol_bar()
        >>> if selected:
        ...     st.write(f"你选择了：{selected}")
    """
    inject_styles()

    # 解析符号列表
    resolved: list[Any] = _resolve_symbols(symbols, _CORE_SYMBOL_CHARS)

    # 获取当前选中状态
    current_selected: Optional[str] = get_selected_symbol()

    # 计算实际列数（取符号数量和 max_cols 的较小值）
    n_cols: int = min(len(resolved), max_cols)
    if n_cols == 0:
        return None

    cols = st.columns(n_cols)

    clicked_char: Optional[str] = None

    for i, sym in enumerate(resolved):
        col_idx: int = i % n_cols
        with cols[col_idx]:
            char: str = _attr(sym, "character", "?")
            emoji: str = _emoji_for(sym)
            label: str = f"{emoji} {char}"

            # 判断是否处于选中状态
            is_selected: bool = (current_selected is not None
                                 and current_selected == char)

            # 选中状态下添加视觉标识
            display_label: str = label
            if is_selected:
                display_label = f":blue-background[{label}]"

            # 唯一 key（避免 Streamlit 重复 ID 冲突）
            key: str = f"fanlang_bar_btn_{char}_{i}"

            # 渲染按钮
            if st.button(
                display_label,
                key=key,
                use_container_width=True,
                type="primary" if is_selected else "secondary",
                on_click=on_symbol_click,
                args=(char,),
            ):
                # 回调已处理 session_state，此处记录返回值
                pass

            # st.button 在回调模式下不直接返回 True，
            # 因此通过检查 session_state 变化来判断点击
            # Streamlit rerun 后 session_state 已更新

    # 返回当前选中符号（由回调写入）
    return get_selected_symbol()


def render_symbol_picker(
    symbols: Optional[list[Any]] = None,
) -> Optional[str]:
    """渲染展开式 FanLang 符号选择器。

    按梯队分组展示所有符号：
    - 一梯队（7 个）：核心高频符号
    - 二梯队（5 个）：扩展符号
    - 三梯队（8 个）：领域符号
    - 四梯队（5 个）：辅助符号

    使用 st.expander 折叠各梯队，减少页面占用。
    点击符号后通过 session_state 记录选中状态。

    Args:
        symbols: 自定义符号列表。传入 None 则从 fanlang.symbols.get_all_symbols()
                 获取全量符号。列表中每个元素应为 dict 或对象。

    Returns:
        本次点击的符号字符（str），未点击任何按钮时返回 None。

    Example:
        >>> selected = render_symbol_picker()
        >>> if selected:
        ...     st.write(f"你选择了：{selected}")
    """
    inject_styles()

    # 解析符号列表：优先从 fanlang 核心包获取全量符号
    if symbols is not None:
        all_symbols: list[Any] = symbols
    else:
        try:
            from fanlang.symbols import get_all_symbols  # type: ignore[import-untyped]
            all_symbols = get_all_symbols()
        except ImportError:
            # fanlang 不可用时使用默认核心符号降级
            all_symbols = _resolve_symbols(None, _CORE_SYMBOL_CHARS)

    # 按梯队分组
    tiered: dict[int, list[Any]] = _group_by_tier(all_symbols)

    # 获取当前选中状态
    current_selected: Optional[str] = get_selected_symbol()

    # 获取各梯队应有数量（用于标签展示）
    tier_counts: dict[int, int] = _tier_symbol_counts()

    for tier in [1, 2, 3, 4]:
        tier_symbols: list[Any] = tiered.get(tier, [])
        if not tier_symbols:
            continue

        label_text: str = _TIER_LABELS.get(
            tier,
            f"梯队 {tier} · {len(tier_symbols)} 个符号",
        )

        with st.expander(label_text, expanded=(tier == 1)):
            # 梯队标签
            count: int = len(tier_symbols)
            expected: int = tier_counts.get(tier, count)
            st.markdown(
                f'<span class="fanlang-tier-label">'
                f'梯队 {tier} · {count}/{expected}</span>',
                unsafe_allow_html=True,
            )

            # 按行渲染符号按钮（每行最多 5 个）
            cols_per_row: int = 5
            for row_start in range(0, len(tier_symbols), cols_per_row):
                row_symbols = tier_symbols[row_start:row_start + cols_per_row]
                n = len(row_symbols)
                cols = st.columns(n)

                for j, sym in enumerate(row_symbols):
                    with cols[j]:
                        char: str = _attr(sym, "character", "?")
                        emoji: str = _emoji_for(sym)
                        name_zh: str = _attr(sym, "name_zh", char)
                        label: str = f"{emoji} {char}"

                        is_selected: bool = (
                            current_selected is not None
                            and current_selected == char
                        )

                        display_label: str = label
                        if is_selected:
                            display_label = f":blue-background[{label}]"

                        key: str = (
                            f"fanlang_picker_t{tier}_r{row_start}_j{j}_{char}"
                        )

                        st.button(
                            display_label,
                            key=key,
                            use_container_width=True,
                            type="primary" if is_selected else "secondary",
                            on_click=on_symbol_click,
                            args=(char,),
                            help=f"{name_zh} ({_attr(sym, 'name_en', '')})",
                        )

    # 返回当前选中符号
    return get_selected_symbol()


def render_terminology_tooltip(term: dict[str, str]) -> None:
    """渲染术语悬停提示卡片。

    以精美的小卡片形式展示英文术语和对应的中文 FanLang 符号翻译。
    适用于在 Streamlit 页面中对特定术语添加辅助说明。

    Args:
        term: 术语数据字典，应包含以下键：
            - ``term_en`` (str): 英文术语。
            - ``term_zh`` (str): 中文 FanLang 符号翻译。

    Example:
        >>> render_terminology_tooltip({
        ...     "term_en": "Translate",
        ...     "term_zh": "翻 - 翻译",
        ... })
    """
    inject_styles()

    term_en: str = term.get("term_en", "")
    term_zh: str = term.get("term_zh", "")

    card_html: str = f"""
    <div class="fanlang-terminology-card">
        <div class="term-en">{term_en}</div>
        <div class="term-zh">{term_zh}</div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)
