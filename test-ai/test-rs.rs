use std::io::stdin;

type Result<T, E = Box<dyn std::error::Error>> = std::result::Result<T, E>;

fn main() -> Result<()> {

    let mut buffer = String::new();

    stdin().read_line(&mut buffer)?;
    let vec: Vec<&str> = buffer.trim_end().split(' ').collect();

    if vec[2]=="2" {
        stdin().read_line(&mut buffer)?;
    }

    loop {
        println!("1");
        stdin().read_line(&mut buffer)?;
    }
}