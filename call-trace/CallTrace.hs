#!/usr/bin/runhaskell

{- Translates call addresses from instrumented executable to
     <function> <file> <line> -}

import Control.Monad
import Control.Exception
import Data.List
import Text.Printf
import System
import System.IO
import System.Posix
import System.IO.Unsafe

type JumpAddr = Int

data JumpType = Call | Return
    deriving (Show, Read, Eq)

data JumpEvent = JumpEvent JumpType JumpAddr JumpAddr
    deriving (Show, Read)

data JumpLine = JumpLine String String Int -- function, file name, line number
    deriving (Show)

data Jump = Jump { jumpType :: JumpType, jumpThis :: JumpLine, jumpSite :: JumpLine }
    deriving (Show)

data Addr2Line = Addr2Line ProcessID Fd Fd -- pid pipeTo pipeFrom
    deriving (Show)

executeAddr2Line input output parentIn parentOut imageName = do
    dupTo input stdInput
    dupTo output stdOutput
    closeFd input
    closeFd output
    closeFd parentIn
    closeFd parentOut
    executeFile "addr2line" True ["--demangle", "--functions", "--basenames", "--exe=" ++ imageName] Nothing

spawnAddr2Line imageName = do
    (a2lIn, toA2L) <- createPipe
    (fromA2L, a2lOut) <- createPipe
    pid <- forkProcess $ executeAddr2Line a2lIn a2lOut fromA2L toA2L imageName
    closeFd a2lIn
    closeFd a2lOut
    return $ Addr2Line pid toA2L fromA2L

killAddr2Line (Addr2Line pid toA2L fromA2L) = do
    closeFd toA2L
    closeFd fromA2L
    getProcessStatus True False pid

addr2Line (Addr2Line _ toA2L fromA2L) addr = do
    fdWrite toA2L $ printf "0x%x\n" addr
    [fun, restOfLine] <- liftM (lines . fst) $ fdRead fromA2L 1024
    let (file, line) = break (==':') restOfLine in -- fail miserably if file name contains ":"
        return $ JumpLine fun file (read $ tail line) 

jumpFromEvent a2l (JumpEvent t x y) = do
    x' <- addr2Line a2l x
    y' <- addr2Line a2l y
    return $ Jump { jumpType = t, jumpThis = x', jumpSite = y' }

dumpJump (Jump _ (JumpLine fun file line) _) = unwords [fun', file, show line]
    where fun' = fst (break (=='(') fun)

dumpTrace jumps = [ (replicate n ' ') ++ dumpJump j | (n, j) <- zip indentLevels jumps, jumpType j == Call ]
    where indent Call = 2
          indent Return = -2
          indentLevels = scanl (+) 0 $ map (indent . jumpType) jumps


dispatch a2l = do
    eof <- isEOF
    if eof then do return [] 
           else do l <- getLine
                   case (reads :: ReadS JumpEvent) l of -- reads is used to filter out only JumpEvent lines
                        [(ev, _)] -> liftM2 (:) (jumpFromEvent a2l ev) (unsafeInterleaveIO $ dispatch a2l)
                        [] -> dispatch a2l

main = do
    [imageName] <- getArgs
    a2l <- spawnAddr2Line imageName
    (liftM dumpTrace (dispatch a2l) >>= (mapM_ putStrLn))
        `finally` killAddr2Line a2l
