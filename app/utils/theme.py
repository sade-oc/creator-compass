"""Theme tokens converted from your Figma export.

This module exposes `THEME` (nested dict) with colors and component tokens
for use across the app. Use these tokens for CSS injection, chart colors,
and any component-level styling. Streamlit's global theme is set in
`.streamlit/config.toml` (also added) and must be restarted to take effect.

Notes:
- Figma used some `rgba(...)` translucent values — Streamlit's `config.toml`
  prefers hex values. We keep the original rgba values here for fine-grained
  CSS uses, while the Streamlit config uses solid hex approximations.
"""

THEME = {
    "colors": {
        "background": {
            "primary": "#000000",
            "card": "rgba(255, 255, 255, 0.05)",
            "cardHover": "rgba(255, 255, 255, 0.08)",
            "input": "rgba(0, 0, 0, 0.5)",
        },
        "brand": {
            "deepBlue": "#1e40af",
            "vibrantPurple": "#8c16db",
            "electricPink": "#ed07b7",
            "brightCyan": "#06b6d4",
            "darkEmerald": "#03822f",
            "amber": "#f59e0b",
        },
        "text": {
            "primary": "#f1f5f9",
            "secondary": "rgba(241, 245, 249, 0.8)",
            "tertiary": "rgba(241, 245, 249, 0.6)",
            "muted": "rgba(241, 245, 249, 0.4)",
        },
        "border": {
            "default": "rgba(255, 255, 255, 0.1)",
            "hover": "rgba(255, 255, 255, 0.2)",
            "focus": "rgba(255, 255, 255, 0.3)",
        },
    },

    "glassmorphism": {
        "backdrop": "backdrop-blur-xl",
        "card": {
            "background": "rgba(255, 255, 255, 0.05)",
            "border": "rgba(255, 255, 255, 0.1)",
        },
    },

    "buttons": {
        "primary": {
            "base": "bg-[#1e40af]/20 hover:bg-[#1e40af]/40",
            "border": "border-[#1e40af]/30 hover:border-[#1e40af]/60",
            "text": "text-[#f1f5f9]",
            "backdrop": "backdrop-blur-xl",
        },
        "secondary": {
            "base": "bg-[#8c16db]/20 hover:bg-[#8c16db]/40",
            "border": "border-[#8c16db]/30 hover:border-[#8c16db]/60",
            "text": "text-[#f1f5f9]",
            "backdrop": "backdrop-blur-xl",
        },
        "accent": {
            "base": "bg-[#ed07b7]/20 hover:bg-[#ed07b7]/40",
            "border": "border-[#ed07b7]/30 hover:border-[#ed07b7]/60",
            "text": "text-[#f1f5f9]",
            "backdrop": "backdrop-blur-xl",
        },
        "info": {
            "base": "bg-[#06b6d4]/20 hover:bg-[#06b6d4]/40",
            "border": "border-[#06b6d4]/30 hover:border-[#06b6d4]/60",
            "text": "text-[#f1f5f9]",
            "backdrop": "backdrop-blur-xl",
        },
        "success": {
            "base": "bg-[#03822f]/20 hover:bg-[#03822f]/40",
            "border": "border-[#03822f]/30 hover:border-[#03822f]/60",
            "text": "text-[#f1f5f9]",
            "backdrop": "backdrop-blur-xl",
        },
        "warning": {
            "base": "bg-[#f59e0b]/20 hover:bg-[#f59e0b]/40",
            "border": "border-[#f59e0b]/30 hover:border-[#f59e0b]/60",
            "text": "text-[#f1f5f9]",
            "backdrop": "backdrop-blur-xl",
        },
        "ghost": {
            "base": "bg-white/5 hover:bg-white/10",
            "border": "border-white/10 hover:border-white/20",
            "text": "text-[#f1f5f9]/60 hover:text-[#f1f5f9]",
            "backdrop": "backdrop-blur-xl",
        },
    },

    "badges": {
        "primary": "bg-[#1e40af]/20 text-[#1e40af] border border-[#1e40af]/30",
        "secondary": "bg-[#8c16db]/20 text-[#8c16db] border border-[#8c16db]/30",
        "accent": "bg-[#ed07b7]/20 text-[#ed07b7] border border-[#ed07b7]/30",
        "info": "bg-[#06b6d4]/20 text-[#06b6d4] border border-[#06b6d4]/30",
        "success": "bg-[#03822f]/20 text-[#03822f] border border-[#03822f]/30",
        "warning": "bg-[#f59e0b]/20 text-[#f59e0b] border border-[#f59e0b]/30",
    },

    "cards": {
        "default": {
            "background": "bg-white/5",
            "border": "border border-white/10",
            "backdrop": "backdrop-blur-xl",
            "hover": "hover:bg-white/8",
        },
        "dark": {
            "background": "bg-black/50",
            "border": "border border-white/10",
            "backdrop": "",
        },
    },

    "inputs": {
        "default": {
            "background": "bg-black/50",
            "border": "border border-white/10",
            "text": "text-[#f1f5f9]",
            "placeholder": "placeholder:text-[#f1f5f9]/40",
            "focus": "focus:border-[#1e40af]/50 focus:outline-none",
        },
    },

    "spacing": {
        "page": "p-4 md:p-8",
        "card": "p-6",
        "cardSmall": "p-4",
        "section": "space-y-6",
        "gap": {
            "xs": "gap-2",
            "sm": "gap-3",
            "md": "gap-4",
            "lg": "gap-6",
        },
    },

    "borderRadius": {
        "default": "rounded-lg",
        "full": "rounded-full",
        "card": "rounded-lg",
    },

    "transitions": {
        "default": "transition-all",
        "colors": "transition-colors",
        "opacity": "transition-opacity",
    },

    "engagement": {
        "high": "#ed07b7",
        "medium": "#06b6d4",
        "low": "#f59e0b",
    },

    "status": {
        "optimal": "#03822f",
        "good": "#f59e0b",
        "average": "rgba(255, 255, 255, 0.1)",
        "positive": "#03822f",
        "negative": "#ed07b7",
    },

    "navigation": {
        "background": "bg-white/5",
        "border": "border-b border-white/10",
        "backdrop": "backdrop-blur-xl",
        "itemActive": "text-[#1e40af]",
        "itemInactive": "text-[#f1f5f9]/60 hover:text-[#f1f5f9]",
    },
}


def get_theme_token(path: str, default=None):
    """Retrieve a token using a dotted path, e.g. 'colors.brand.deepBlue'.

    Returns default if the path is not found.
    """
    parts = path.split('.')
    cur = THEME
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return default
    return cur
