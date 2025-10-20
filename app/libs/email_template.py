def forgot_password_template(first_name, last_name, otp):
    return f"""
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: #f4f8f6;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
                overflow: hidden;
            }}
            .header {{
                background-color: #e6f4ea;
                padding: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-bottom: 2px solid #28a745;
            }}
            .header img {{
                height: 50px;
                margin-right: 12px;
            }}
            .header-title {{
                padding-top: 15px;
                font-size: 24px;
                font-weight: 600;
                color: #28a745;
            }}
            .title {{
                background-color: #28a745;
                color: white;
                text-align: center;
                padding: 14px;
                font-size: 20px;
                font-weight: 500;
            }}
            .content {{
                padding: 30px;
                color: #333;
            }}
            .content p {{
                margin: 14px 0;
                line-height: 1.6;
                font-size: 15px;
            }}
            .otp-box {{
                background-color: #e0f6e7;
                border: 1px solid #b8e2c7;
                color: #155724;
                font-size: 26px;
                font-weight: bold;
                padding: 12px 30px;
                border-radius: 6px;
                display: inline-block;
                margin-top: 10px;
            }}
            .footer {{
                background-color: #f9f9f9;
                color: #777;
                font-size: 12px;
                text-align: center;
                padding: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="cid:logo_image" alt="Logo" />
                <div class="header-title">DailyVeg</div>
            </div>
            <div class="title">Password Reset</div>
            <div class="content">
                <p>Hi <strong>{first_name} {last_name}</strong>,</p>
                <p>We received a request to reset your password for your DailyVeg account.</p>
                <p>Your OTP is:</p>
                <div class="otp-box">{otp}</div>
                <p>This OTP is valid for 10 minutes.</p>
                <p>If you didn’t request a password reset, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                &copy; 2025 DailyVeg. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """


def send_password_template(first_name, last_name, password):
    return f"""
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: #f4f8f6;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
                overflow: hidden;
            }}
            .header {{
                background-color: #e6f4ea;
                padding: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-bottom: 2px solid #28a745;
            }}
            .header img {{
                height: 50px;
                margin-right: 12px;
            }}
            .header-title {{
                padding-top: 15px;
                font-size: 24px;
                font-weight: 600;
                color: #28a745;
            }}
            .title {{
                background-color: #28a745;
                color: white;
                text-align: center;
                padding: 14px;
                font-size: 20px;
                font-weight: 500;
            }}
            .content {{
                padding: 30px;
                color: #333;
            }}
            .content p {{
                margin: 14px 0;
                line-height: 1.6;
                font-size: 15px;
            }}
            .password-box {{
                background-color: #e0f6e7;
                border: 1px solid #b8e2c7;
                color: #155724;
                font-size: 20px;
                font-weight: bold;
                padding: 12px 30px;
                border-radius: 6px;
                display: inline-block;
                word-break: break-all;
                margin-top: 10px;
            }}
            .footer {{
                background-color: #f9f9f9;
                color: #777;
                font-size: 12px;
                text-align: center;
                padding: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="cid:logo_image" alt="Logo" />
                <div class="header-title">DailyVeg</div>
            </div>
            <div class="title">Your Account Password</div>
            <div class="content">
                <p>Hi <strong>{first_name} {last_name}</strong>,</p>
                <p>As per your request, here is the password for your DailyVeg account:</p>
                <div class="password-box">{password}</div>
                <p>Please keep this password secure and do not share it with anyone.</p>
                <p>If you did not request this, we recommend changing your password immediately.</p>
            </div>
            <div class="footer">
                &copy; 2025 DailyVeg. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
