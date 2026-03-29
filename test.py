import os

def save_my_files(directory=".", output_file="my_code_collection.txt"):
    """
    'M'과 'U' 표시된 파일들의 내용을 모두 읽어서 하나의 파일로 저장합니다.
    """
    files_to_read = {
        'M': [
            'app/templates/base.html',
            'app/templates/create_post.html',
            'app/templates/post.html',
            'app/__init__.py',
            'app/models.py',
            'app/routes.py',
            'config.py',
            'run.py'
        ],
        'U': [
            'app/templates/login.html',
            'app/templates/register.html',
            'app/content_detector.py',
        ]
    }
    
    with open(output_file, 'w', encoding='utf-8') as output:
        output.write("=== 작성한 코드 모음 ===\n\n")
        
        for status, files in files_to_read.items():
            for filename in files:
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                        output.write(f"\n{'='*50}\n")
                        output.write(f"파일명: {filename} ({status})\n")
                        output.write(f"{'='*50}\n")
                        output.write(content)
                        output.write(f"\n{'='*50}\n")
                        print(f"{filename} 파일 내용 저장 완료")
                except FileNotFoundError:
                    print(f"\n{filename} 파일을 찾을 수 없습니다.")
                except Exception as e:
                    print(f"\n{filename} 파일 읽기 중 오류 발생: {str(e)}")
    
    print(f"\n모든 파일 내용이 '{output_file}'에 저장되었습니다.")

if __name__ == "__main__":
    save_my_files()